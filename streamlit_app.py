import streamlit as st
import requests
import json
import sqlite3
import pandas as pd
from pdfminer.high_level import extract_text
from PIL import Image

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
API_KEY = "YOUR_API_KEY"

# Function to call API
def get_resume_analysis(resume_text):
    prompt = f"""
    You are an expert resume analyzer. Extract and output the following information strictly in JSON format:
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

    response = requests.post(API_URL, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        try:
            return json.loads(response.json()["choices"][0]["message"]["content"])
        except (KeyError, json.JSONDecodeError):
            return {"error": "Invalid JSON response from API."}
    else:
        return {"error": f"API Error {response.status_code}"}

# ------------------------
# PDF Text Extraction
# ------------------------
def extract_text_from_pdf(uploaded_file):
    if uploaded_file is not None:
        with open("temp_resume.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())  # Save uploaded file locally
        extracted_text = extract_text("temp_resume.pdf")
        return extracted_text
    else:
        return "No file uploaded."

# ------------------------
# Streamlit App
# ------------------------
st.set_page_config(page_title="Smart Resume Analyzer", page_icon="\ud83d\udcc4")

st.sidebar.title("User Mode")
mode = st.sidebar.selectbox("Select Mode", ["User", "Admin"])

if mode == "User":
    st.title("\ud83d\udcc4 Smart Resume Analyzer")
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
                basic_info = result.get("basic_info", {})
                skills = result.get("skills", {})
                courses = result.get("course_recommendations", [])
                resume_score = int(result.get("resume_score", "70").split("/")[0])

                # Display results
                st.header("Basic Info")
                st.write(basic_info)
                st.header("Skills")
                st.write(skills)
                st.header("Recommended Courses")
                for course in courses:
                    st.markdown(f"- **{course['platform']}**: [{course['course_name']}]({course['link']})")
                st.header("Resume Score")
                st.metric(label="Score", value=f"{resume_score}/100")

                # Save to database
                cursor.execute('''
                    INSERT INTO user_data (name, email, resume_score, skills, recommended_skills, courses, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
                ''', (
                    basic_info.get("name", "N/A"),
                    basic_info.get("email", "N/A"),
                    resume_score,
                    ", ".join(skills.get("current_skills", [])),
                    ", ".join(skills.get("recommended_skills", [])),
                    ", ".join([course['course_name'] for course in courses])
                ))
                conn.commit()

elif mode == "Admin":
    st.title("\ud83d\udd10 Admin Dashboard")
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
