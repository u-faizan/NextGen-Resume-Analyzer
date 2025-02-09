import streamlit as st
import requests
import json
import sqlite3
import pandas as pd
import re
from pdfminer.high_level import extract_text

# ------------------------
# Database Setup
# ------------------------
conn = sqlite3.connect('resume_data.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        resume_score INTEGER,
        skills TEXT,
        recommended_skills TEXT,
        courses TEXT,
        timestamp TEXT
    )
''')
conn.commit()

# ------------------------
# API Configuration
# ------------------------
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = st.secrets["API_KEY"]

# Function to call API
def get_resume_analysis(resume_text):
    prompt = f"""
    You are an expert resume analyzer. Extract and return the following information strictly in JSON format:
    {{
        "basic_info": {{ "name": string, "email": string }},
        "skills": {{ "current_skills": list, "recommended_skills": list }},
        "course_recommendations": list,
        "resume_score": string
    }}
    Resume text:
    '''{resume_text}'''
    """

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek/deepseek-r1-distill-llama-70b:free",
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        try:
            # Extract JSON content from response
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                json_text = json_match.group(0)
                return json.loads(json_text)
            else:
                return {"error": "No valid JSON found in API response."}
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response from API."}
    else:
        return {"error": f"API Error {response.status_code}: {response.json().get('error', {}).get('message', 'Unknown error')}"}

# ------------------------
# PDF Text Extraction
# ------------------------
def extract_text_from_pdf(uploaded_file):
    if uploaded_file is not None:
        with open("temp_resume.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())  # Save uploaded file locally
        extracted_text = extract_text("temp_resume.pdf")
        return extracted_text.strip() if extracted_text else "No text extracted."
    return "No file uploaded."

# ------------------------
# Streamlit App
# ------------------------
st.set_page_config(page_title="Smart Resume Analyzer", page_icon="📄")

st.sidebar.title("User Mode")
mode = st.sidebar.selectbox("Select Mode", ["User", "Admin"])

if mode == "User":
    st.title("📄 Smart Resume Analyzer")
    uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"])

    if uploaded_file:
        st.success("File uploaded successfully!")

        resume_text = extract_text_from_pdf(uploaded_file)
        st.subheader("Extracted Resume Text")
        st.text(resume_text[:500] + "...")

        if st.button("Analyze Resume"):
            with st.spinner("Analyzing resume..."):
                result = get_resume_analysis(resume_text)

            if "error" in result:
                st.error(result["error"])
            else:
                st.success("Resume Analyzed Successfully!")

                # Extract and display results
                basic_info = result.get("basic_info", {})
                skills = result.get("skills", {})
                courses = result.get("course_recommendations", [])
                resume_score_raw = result.get("resume_score", "70/100")

                # Extract resume score safely
                resume_score = 70  # Default
                if isinstance(resume_score_raw, str):
                    resume_score_match = re.search(r'\d+', resume_score_raw)
                    if resume_score_match:
                        resume_score = int(resume_score_match.group())

                # Display extracted information
                st.header("Basic Info")
                st.write(f"**Name:** {basic_info.get('name', 'Not Found')}")
                st.write(f"**Email:** {basic_info.get('email', 'Not Found')}")

                st.header("Skills")
                current_skills = skills.get("current_skills", [])
                recommended_skills = skills.get("recommended_skills", [])

                st.write(f"**Current Skills:** {', '.join(current_skills) if current_skills else 'Not Found'}")
                st.write(f"**Recommended Skills:** {', '.join(recommended_skills) if recommended_skills else 'Not Found'}")

                st.header("Recommended Courses")
                if isinstance(courses, list) and courses:
                    for course in courses:
                        if isinstance(course, dict) and all(k in course for k in ["platform", "course_name", "link"]):
                            st.markdown(f"- **{course['platform']}**: [{course['course_name']}]({course['link']})")
                        else:
                            st.warning("Unexpected course data format.")
                else:
                    st.warning("No course recommendations available.")

                st.header("Resume Score")
                st.metric(label="Score", value=f"{resume_score}/100")

                # Save to database
                cursor.execute('''
                    INSERT INTO user_data (name, email, resume_score, skills, recommended_skills, courses, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
                ''', (
                    basic_info.get("name", "Unknown"),
                    basic_info.get("email", "Unknown"),
                    resume_score,
                    ", ".join(current_skills),
                    ", ".join(recommended_skills),
                    ", ".join([course['course_name'] for course in courses if isinstance(course, dict)])
                ))
                conn.commit()

elif mode == "Admin":
    st.title("🔐 Admin Dashboard")
    admin_user = st.text_input("Username")
    admin_pass = st.text_input("Password", type="password")

    if st.button("Login"):
        if admin_user == "admin" and admin_pass == "admin123":
            st.success("Logged in as Admin")

            # Fetch data from DB
            cursor.execute("SELECT * FROM user_data")
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=['ID', 'Name', 'Email', 'Resume Score', 'Skills', 'Recommended Skills', 'Courses', 'Timestamp'])

            st.header("User Data")
            st.dataframe(df)

            # Visualizations
            st.subheader("Resume Score Distribution")
            st.bar_chart(df['Resume Score'])
        else:
            st.error("Invalid Admin Credentials")
