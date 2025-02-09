import streamlit as st
import requests
import json
import sqlite3
import pandas as pd
from pdfminer.high_level import extract_text
import re

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
API_KEY = st.secrets["API_KEY"]  # Securely access the API key

def get_resume_analysis(resume_text):
    prompt = f"""
    You are an expert resume analyzer. Extract and output the following information strictly in JSON format. Do not include any explanations, comments, or additional text outside the JSON block.

    Allowed JSON keys are ONLY the following. Do not create new keys or modify these key names:
    "basic_info", "skills", "course_recommendations", "appreciation", "resume_tips", "resume_score", "ai_resume_summary", "matching_job_roles", "ats_keywords", "project_suggestions"

    Here’s the required JSON structure:
    {{
        "basic_info": {{
            "name": string,
            "email": string,
            "mobile": string,
            "address": string
        }},
        "skills": {{
            "current_skills": list of at least 5 key skills,
            "recommended_skills": list of at least 5 skills to improve the resume
        }},
        "course_recommendations": list of at least 5 relevant courses with the following details for each course:
        {{
            "platform": string,
            "course_name": string,
            "link": valid URL
        }},
        "appreciation": list of at least 5 personalized positive comments starting with "You have..." or "Your...",
        "resume_tips": list of at least 5 constructive feedback points for resume improvement,
        "resume_score": string (score in "XX/100" format),
        "ai_resume_summary": string,
        "matching_job_roles": list of 2-3 job roles,
        "ats_keywords": list of at least 5 industry-relevant keywords,
        "project_suggestions": list of at least 3 one-line strings.
    }}

    Return only valid JSON and nothing else.

    Here is the resume text:
    \"\"\"{resume_text}\"\"\"
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
            raw_response = response.json()["choices"][0]["message"]["content"]
            # Extract the JSON block using regex
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if json_match:
                json_text = json_match.group(0)
                return json.loads(json_text)
            else:
                return {"error": "No valid JSON found in API response."}
        except (KeyError, json.JSONDecodeError):
            return {"error": "Invalid JSON response from API."}
    else:
        return {"error": f"API Error {response.status_code}: {response.text}"}

# ------------------------
# PDF Text Extraction
# ------------------------
def extract_text_from_pdf(uploaded_file):
    if uploaded_file is not None:
        with open("temp_resume.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())
        return extract_text("temp_resume.pdf")
    else:
        return ""

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
                basic_info = result.get("basic_info", {})
                skills = result.get("skills", {})

                # --- Resume Score Extraction ---
                resume_score_raw = result.get("resume_score", "70/100")
                if isinstance(resume_score_raw, int):
                    resume_score = resume_score_raw
                elif isinstance(resume_score_raw, str):
                    resume_score_match = re.search(r'\d+', resume_score_raw)
                    resume_score = int(resume_score_match.group()) if resume_score_match else 70
                else:
                    resume_score = 70

                # --- Course Recommendations Handling ---
                course_recommendations = result.get("course_recommendations", [])
                if isinstance(course_recommendations, str):
                    try:
                        course_recommendations = json.loads(course_recommendations)
                        if not isinstance(course_recommendations, list):
                            course_recommendations = [course_recommendations]
                    except json.JSONDecodeError:
                        course_recommendations = [course_recommendations]
                elif not isinstance(course_recommendations, list):
                    course_recommendations = []

                # Displaying the results:
                st.header("Basic Info")
                st.write(basic_info)
                st.header("Skills")
                st.write(skills)
                st.header("Recommended Courses")
                for course in course_recommendations:
                    if isinstance(course, dict):
                        platform = course.get("platform", "Unknown Platform")
                        course_name = course.get("course_name", "Unknown Course")
                        link = course.get("link", "#")
                        st.markdown(f"- **{platform}**: [{course_name}]({link})")
                    else:
                        st.markdown(f"- {course}")
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
                    ", ".join([course.get("course_name", "") if isinstance(course, dict) else str(course)
                               for course in course_recommendations])
                ))
                conn.commit()

elif mode == "Admin":
    st.title("🔐 Admin Dashboard")
    admin_user = st.text_input("Username")
    admin_pass = st.text_input("Password", type="password")

    if st.button("Login"):
        if admin_user == "admin" and admin_pass == "admin123":
            st.success("Logged in as Admin")
            cursor.execute("SELECT * FROM user_data")
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=['ID', 'Name', 'Email', 'Resume Score', 'Skills', 'Recommended Skills', 'Courses', 'Timestamp'])
            st.header("User Data")
            st.dataframe(df)
            st.subheader("Resume Score Distribution")
            st.bar_chart(df['Resume Score'])
        else:
            st.error("Invalid Admin Credentials")
