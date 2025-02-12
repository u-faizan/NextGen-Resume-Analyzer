import streamlit as st
from PIL import Image
import requests
import json
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from pdfminer.high_level import extract_text
import re
import os
import base64

# ===========================
# Custom CSS for Modern Look
# ===========================
def load_css(theme="light"):
    if theme == "dark":
        css = """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
            body { font-family: 'Roboto', sans-serif; }
            .header { padding: 20px; text-align: center; background-color: #333333; color: white; }
            .card { background-color: #222222; padding: 20px; margin: 10px 0; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.5); color: white; }
            h1, h2, h3, h4 { color: #FFFFFF; }
            p { color: #CCCCCC; }
        </style>
        """
    else:  # light theme
        css = """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
            body { font-family: 'Roboto', sans-serif; }
            .header { padding: 20px; text-align: center; background-color: #F0F0F0; color: #15967D; }
            .card { background-color: #FFFFFF; padding: 20px; margin: 10px 0; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
            h1, h2, h3, h4 { color: #15967D; }
            p { color: #333333; }
        </style>
        """
    st.markdown(css, unsafe_allow_html=True)

# ===========================
# Sidebar Styling & Theme Toggle
# ===========================
# Theme toggle in sidebar
theme_choice = st.sidebar.radio("Theme", options=["Light", "Dark"], index=0)
load_css(theme="dark" if theme_choice=="Dark" else "light")

# Sidebar Navigation
nav_option = st.sidebar.radio("Navigation", options=["User Mode", "Admin Mode", "Download Results"], index=0)

# Additional sidebar styling for consistent look
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            background-color: #15967D !important;
        }
        [data-testid="stSidebar"] * {
            color: white !important;
        }
        /* For select boxes in sidebar, force black text */
        div[data-baseweb="select"] {
            color: black !important;
        }
        div[data-baseweb="select"] * {
            color: black !important;
        }
        .stButton > button {
            background-color: #15967D !important;
            color: white !important;
            font-size: 16px;
            font-weight: bold;
            padding: 8px 20px;
            border-radius: 5px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ===========================
# Helper Functions
# ===========================
def extract_json(response_text):
    """Extracts JSON from a string using regex."""
    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
    if json_match:
        json_text = json_match.group(0)
        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            st.error("Error: The extracted JSON is not valid.")
            return {}
    else:
        st.error("Error: No valid JSON found in the response.")
        return {}

def validate_resume(text):
    """Checks if the extracted text contains common resume keywords."""
    keywords = ["education", "experience", "skills", "projects", "certifications"]
    return any(keyword in text.lower() for keyword in keywords)

def get_top_skills(skill_series, top_n=5):
    """Group and count skills, grouping extras under 'Others'."""
    skill_counts = pd.Series(", ".join(skill_series).split(", ")).value_counts()
    if len(skill_counts) > top_n:
        top_skills = skill_counts.head(top_n)
        top_skills.loc["Others"] = skill_counts[top_n:].sum()
        return top_skills
    return skill_counts

# ===========================
# Database Setup
# ===========================
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

# ===========================
# API Configuration & Resume Analysis
# ===========================
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = st.secrets["API_KEY"]

def get_resume_analysis(resume_text):
    prompt = f"""
You are an expert resume analyzer. Extract and output the following information strictly in JSON format. Do not include any explanations, comments, or additional text outside the JSON block.

Evaluation Criteria for Resume Score:
- Formatting and structure (clear sections, bullet points)
- ATS Optimization (use of industry-relevant keywords)
- Content Quality (clarity, conciseness, grammar)
- Relevance (matching skills and experience)
- Readability and presentation

Return the JSON structure as follows:
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
    "course_recommendations": list of at least 10 courses with details as:
    {{
        "platform": string,
        "course_name": string,
        "link": valid URL
    }},
    "appreciation": list of at least 5 personalized positive comments to acknowledge the candidate's strengths,
    "resume_tips": list of at least 5 specific suggestions for improvement,
    "resume_score": string (score in "XX/100" format based on the evaluation criteria),
    "ai_resume_summary": string (a concise summary of the candidate's experience, skills, and expertise for ATS optimization),
    "matching_job_roles": list of 2-3 job roles that match the candidate's skills,
    "ats_keywords": list of at least 5 industry-relevant keywords missing from the resume to improve ATS ranking,
    "project_suggestions": {{
        "improvement_tips": list of 2-3 tips to enhance existing projects,
        "new_project_recommendations": list of 2-3 suggested projects
    }}
}}

Ensure the JSON is valid before outputting.

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
            data = extract_json(raw_response)
            if not data:
                st.warning("No valid JSON found in API response. Please try again.")
                return {"error": "No valid JSON found in API response."}
            return data
        except Exception as e:
            st.error(f"Error during JSON extraction: {e}")
            st.warning("Something went wrong while processing your request. Try again, it might work now.")
            return {"error": "Invalid JSON response from API."}
    else:
        st.error(f"API Error {response.status_code}: {response.text}")
        st.warning("There was an issue with the API response. Try again, it might work this time.")
        return {"error": f"API Error {response.status_code}: {response.text}"}

# ===========================
# PDF Text Extraction
# ===========================
def extract_text_from_pdf(uploaded_file):
    if uploaded_file is not None:
        with open("temp_resume.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())
        return extract_text("temp_resume.pdf")
    else:
        return ""

# ===========================
# Main App
# ===========================
# Header with Branding
st.markdown("""
<div class="header">
    <img src="https://via.placeholder.com/50" style="vertical-align:middle; margin-right:10px;">
    <span style="font-size: 2.5em; font-weight: bold;">NextGen Resume Analyzer</span>
</div>
""", unsafe_allow_html=True)

if nav_option == "User Mode":
    st.title("User Dashboard")
    uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"])
    if uploaded_file:
        st.success("File uploaded successfully!")
        resume_text = extract_text_from_pdf(uploaded_file)
        st.markdown("<br>Click the <span style='color: #15967D; font-weight: bold;'>Analyze Resume</span> button to proceed.", unsafe_allow_html=True)
        
        if not validate_resume(resume_text):
            st.error("❌ The uploaded document does not appear to be a valid resume. Please upload a proper resume file.")
        else:
            if st.button("Analyze Resume"):
                with st.spinner("Analyzing resume..."):
                    result = get_resume_analysis(resume_text)
                if "error" in result:
                    st.error(result["error"])
                else:
                    # Greeting & Basic Info Section with Card Design
                    basic_info = result.get("basic_info", {})
                    if basic_info.get("name"):
                        st.markdown(f"<h2>Hello, {basic_info.get('name')}!</h2>", unsafe_allow_html=True)
                    st.markdown("<h3>Basic Info</h3>", unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class="card">
                        <strong>Name:</strong> {basic_info.get('name', 'N/A')}<br>
                        <strong>Email:</strong> {basic_info.get('email', 'N/A')}<br>
                        <strong>Mobile:</strong> {basic_info.get('mobile', 'N/A')}<br>
                        <strong>Address:</strong> {basic_info.get('address', 'N/A')}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # AI Resume Summary Section
                    st.markdown("<h3>AI Resume Summary</h3>", unsafe_allow_html=True)
                    st.markdown("<p style='font-size:16px; line-height:1.5; color:#333333;'>A concise summary of your experience, skills, and expertise, tailored for ATS optimization.</p>", unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class="card" style="border-left: 4px solid #15967D;">
                        {result.get('ai_resume_summary', '')}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Resume Score Section
                    st.markdown("<h3>Resume Score</h3>", unsafe_allow_html=True)
                    resume_score_raw = result.get("resume_score", "70/100")
                    if isinstance(resume_score_raw, int):
                        resume_score = resume_score_raw
                    elif isinstance(resume_score_raw, str):
                        resume_score_match = re.search(r'\d+', resume_score_raw)
                        resume_score = int(resume_score_match.group()) if resume_score_match else 70
                    else:
                        resume_score = 70
                    st.metric(label="Score", value=f"{resume_score}/100")
                    st.markdown("<p><em>Note:</em> The score is derived from structure, keyword usage, clarity, and overall presentation.</p>", unsafe_allow_html=True)
                    
                    # Skills Section arranged in Cards using columns
                    st.markdown("<h3>Skills</h3>", unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("<h4 style='color:#15967D;'>Current Skills</h4>", unsafe_allow_html=True)
                        with st.container():
                            for skill in result.get("skills", {}).get("current_skills", []):
                                st.markdown(f"- {skill}")
                    with col2:
                        st.markdown("<h4 style='color:#15967D;'>Recommended Skills</h4>", unsafe_allow_html=True)
                        with st.container():
                            for skill in result.get("skills", {}).get("recommended_skills", []):
                                st.markdown(f"- {skill}")
                    
                    # Recommended Courses Section with Slider
                    st.markdown("<h3>Recommended Courses</h3>", unsafe_allow_html=True)
                    num_courses = st.slider("Select number of course recommendations to display:", min_value=1, max_value=10, value=5, key="courses_slider")
                    st.markdown("Courses suggested to help you enhance your skillset:")
                    for course in result.get("course_recommendations", [])[:num_courses]:
                        if isinstance(course, dict):
                            platform = course.get("platform", "Unknown Platform")
                            course_name = course.get("course_name", "Unknown Course")
                            link = course.get("link", "#")
                            st.markdown(f"- <span style='color:#15967D; font-weight:bold;'>{platform}</span>: [{course_name}]({link})", unsafe_allow_html=True)
                        else:
                            st.markdown(f"- {course}")
                    
                    # Appreciation Section
                    st.markdown("<h3>Appreciation</h3>", unsafe_allow_html=True)
                    st.markdown("Positive comments acknowledging your strengths:")
                    for comment in result.get("appreciation", []):
                        st.markdown(f"- {comment}")
                    
                    # Resume Tips Section
                    st.markdown("<h3>Resume Tips</h3>", unsafe_allow_html=True)
                    st.markdown("Constructive suggestions for improving your resume:")
                    for tip in result.get("resume_tips", []):
                        st.markdown(f"- {tip}")
                    
                    # Matching Job Roles Section
                    st.markdown("<h3>Matching Job Roles</h3>", unsafe_allow_html=True)
                    st.markdown("Job roles that align with your skills and experience:")
                    for role in result.get("matching_job_roles", []):
                        st.markdown(f"- {role}")
                    
                    # ATS Keywords Section
                    st.markdown("<h3>ATS Keywords</h3>", unsafe_allow_html=True)
                    st.markdown("Industry-relevant keywords for better ATS performance:")
                    ats_keywords = result.get("ats_keywords", [])
                    if isinstance(ats_keywords, list):
                        for keyword in ats_keywords:
                            st.markdown(f"- {keyword}")
                    else:
                        st.json(ats_keywords)
                    
                    # Project Suggestions Section with Expanders and Colored Subheadings
                    st.markdown("<h3>Project Suggestions</h3>", unsafe_allow_html=True)
                    with st.expander("<span style='color:#15967D;'>Improvement Tips for Existing Projects</span>", expanded=True):
                        for tip in result.get("project_suggestions", {}).get("improvement_tips", []):
                            st.markdown(f"- {tip}")
                    with st.expander("<span style='color:#15967D;'>New Project Recommendations</span>", expanded=True):
                        for proj in result.get("project_suggestions", {}).get("new_project_recommendations", []):
                            st.markdown(f"- {proj}")
                    
                    # --- Download/Export Section ---
                    st.markdown("<h3>Export Your Details</h3>", unsafe_allow_html=True)
                    export_data = {
                        "Basic Info": basic_info,
                        "AI Resume Summary": result.get("ai_resume_summary", ""),
                        "Resume Score": resume_score,
                        "Skills": result.get("skills", {}),
                        "Recommended Courses": result.get("course_recommendations", []),
                        "Appreciation": result.get("appreciation", []),
                        "Resume Tips": result.get("resume_tips", []),
                        "Matching Job Roles": result.get("matching_job_roles", []),
                        "ATS Keywords": result.get("ats_keywords", []),
                        "Project Suggestions": result.get("project_suggestions", {})
                    }
                    export_json = json.dumps(export_data, indent=4)
                    st.download_button("Download Details as JSON", data=export_json, file_name="resume_analysis.json", mime="application/json")

                    # --- Save to Database ---
                    cursor.execute('''
                        INSERT INTO user_data (name, email, resume_score, skills, recommended_skills, courses, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
                    ''', (
                        basic_info.get("name", "N/A"),
                        basic_info.get("email", "N/A"),
                        resume_score,
                        ", ".join(result.get("skills", {}).get("current_skills", [])),
                        ", ".join(result.get("skills", {}).get("recommended_skills", [])),
                        ", ".join([course.get("course_name", "") if isinstance(course, dict) else str(course)
                                   for course in result.get("course_recommendations", [])])
                    ))
                    conn.commit()

elif nav_option == "Admin Mode":
    st.title("🔐 Admin Dashboard")
    admin_user = st.text_input("Username")
    admin_pass = st.text_input("Password", type="password")
    if st.button("Login"):
        if admin_user == st.secrets["user_name"] and admin_pass == st.secrets["pass"]:
            st.success("Logged in as Admin")
            cursor.execute("SELECT * FROM user_data")
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=['ID', 'Name', 'Email', 'Resume Score', 'Skills', 'Recommended Skills', 'Courses', 'Timestamp'])
            st.markdown("<h3>User Data</h3>", unsafe_allow_html=True)
            st.dataframe(df)
            st.markdown("<h3>Resume Score Distribution</h3>", unsafe_allow_html=True)
            st.bar_chart(df['Resume Score'])
            
            st.markdown("<h3>Top Skills Overview</h3>", unsafe_allow_html=True)
            def get_top_skills(skill_series, top_n=5):
                skill_counts = pd.Series(", ".join(skill_series).split(", ")).value_counts()
                if len(skill_counts) > top_n:
                    top_skills = skill_counts.head(top_n)
                    top_skills.loc["Others"] = skill_counts[top_n:].sum()
                else:
                    top_skills = skill_counts
                return top_skills
            
            top_current_skills = get_top_skills(df['Skills'])
            top_recommended_skills = get_top_skills(df['Recommended Skills'])
            
            col1, col2 = st.columns(2)
            with col1:
                fig1, ax1 = plt.subplots(figsize=(6,6))
                top_current_skills.plot.pie(ax=ax1, autopct='%1.1f%%', startangle=140, wedgeprops={'edgecolor':'white'})
                ax1.set_ylabel('')
                ax1.set_title("Current Skills")
                st.pyplot(fig1)
            with col2:
                fig2, ax2 = plt.subplots(figsize=(6,6))
                top_recommended_skills.plot.pie(ax=ax2, autopct='%1.1f%%', startangle=140, wedgeprops={'edgecolor':'white'})
                ax2.set_ylabel('')
                ax2.set_title("Recommended Skills")
                st.pyplot(fig2)
        
        else:
            st.error("Invalid Admin Credentials")
    
elif nav_option == "Download Results":
    st.title("Export Data")
    cursor.execute("SELECT * FROM user_data")
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=['ID', 'Name', 'Email', 'Resume Score', 'Skills', 'Recommended Skills', 'Courses', 'Timestamp'])
    export_json = df.to_json(orient="records", indent=4)
    st.download_button("Download All Data as JSON", data=export_json, file_name="user_data.json", mime="application/json")
