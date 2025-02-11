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
API_KEY = st.secrets["API_KEY"]  # Securely accessing the API key from secrets

def validate_resume(text):
    """Checks if the extracted text contains key resume-like elements."""
    keywords = ["education", "experience", "skills", "projects", "certifications"]
    return any(keyword in text.lower() for keyword in keywords)

def get_resume_analysis(resume_text):
    prompt = f"""
    You are an expert resume analyzer. Extract and return the following information **strictly in JSON format**. **Do not include any explanations, comments, or additional text** outside the JSON block.

    **Evaluation Criteria:**
    - Content Quality: Clear and well-structured information
    - ATS Optimization: Proper use of industry-relevant keywords
    - Resume Structure: Logical flow of sections (Education, Experience, Skills, etc.)
    - Readability: Concise formatting, bullet points, minimal clutter

    **Return the JSON structure as follows:**
    {{
        "basic_info": {{
            "name": string,
            "email": string,
            "mobile": string,
            "address": string
        }},
        "skills": {{
            "current_skills": list of at least 5 key skills,
            "recommended_skills": list of at least 5 skills for improvement
        }},
        "course_recommendations": list of at least 5 courses with:
        {{
            "platform": string,
            "course_name": string,
            "link": valid URL
        }},
        "appreciation": list of at least 5 personalized positive comments,
        "resume_tips": list of at least 5 specific suggestions for improvement,
        "resume_score": string (score in "XX/100" format based on evaluation criteria),
        "ai_resume_summary": string (concise summary of experience, skills, and expertise for ATS optimization),
        "matching_job_roles": list of 2-3 job roles that align with the candidate's skills,
        "ats_keywords": {{
            "existing_keywords": list of relevant ATS keywords already present,
            "missing_keywords": list of relevant ATS keywords that should be added
        }},
        "project_suggestions": {{
            "improvement_tips": list of 2-3 tips to enhance existing projects,
            "new_project_recommendations": list of 2-3 suggested projects to strengthen the resume
        }}
    }}

    **Return only valid JSON and nothing else.**
    Here is the resume text:
    "{resume_text}"
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
            return json.loads(response.json()["choices"][0]["message"]["content"])
        except (KeyError, json.JSONDecodeError):
            return {"error": "Invalid JSON response from API."}
    else:
        return {"error": f"API Error {response.status_code}: {response.text}"}

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
        resume_text = extract_text(uploaded_file)
        if not validate_resume(resume_text):
            st.error("❌ The uploaded document does not appear to be a resume. Please upload a valid resume.")
        else:
            st.subheader("Extracted Resume Preview")
            st.text(resume_text[:500] + "...")
            if st.button("Analyze Resume"):
                with st.spinner("Analyzing resume..."):
                    result = get_resume_analysis(resume_text)
                if "error" in result:
                    st.error(result["error"])
                else:
                    st.header("Basic Info")
                    st.json(result["basic_info"])

                    st.header("Skills")
                    st.json(result["skills"])

                    st.header("Recommended Courses")
                    for course in result["course_recommendations"]:
                        st.markdown(f"- **{course['platform']}**: [{course['course_name']}]({course['link']})")

                    st.header("Appreciation")
                    for comment in result["appreciation"]:
                        st.markdown(f"- {comment}")

                    st.header("Resume Tips")
                    for tip in result["resume_tips"]:
                        st.markdown(f"- {tip}")

                    st.header("AI Resume Summary")
                    st.write(result["ai_resume_summary"])

                    st.header("Matching Job Roles")
                    st.write(", ".join(result["matching_job_roles"]))

                    st.header("ATS Keywords")
                    st.json(result["ats_keywords"])

                    st.header("Project Suggestions")
                    st.json(result["project_suggestions"])

                    st.header("Resume Score")
                    st.metric(label="Score", value=result["resume_score"])
