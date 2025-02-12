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
    """Groups and counts skills, grouping extras under 'Others'."""
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
# API Configuration and Resume Analysis
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
    "course_recommendations": list of at least 5 courses with details as:
    {{
        "platform": string,
        "course_name": string,
        "link": valid URL
    }},
    "appreciation": list of at least 5 personalized positive comments,
    "resume_tips": list of at least 5 suggestions for improvement,
    "resume_score": string (score in "XX/100" format),
    "ai_resume_summary": string (a concise summary for ATS optimization),
    "matching_job_roles": list of 2-3 job roles,
    "ats_keywords": list of at least 5 industry-relevant keywords,
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
            st.warning("Something went wrong. Try again, it might work now.")
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
# Header with Branding: Project Name in a border matching sidebar style
st.markdown("""
<div style="background-color:#15967D; padding:20px; text-align:left; border-bottom: 3px solid #15967D;">
    <span style="font-size: 2.5em; font-weight: bold; color:white;"> 📝 NextGen Resume Analyzer</span>
</div>
""", unsafe_allow_html=True)

# Sidebar remains unchanged
st.sidebar.title("User Mode")
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            background-color: #15967D !important;
            color: white !important;
        }
        [data-testid="stSidebar"] * {
            color: white !important;
        }
        div[data-baseweb="select"] {
            color: black !important;
        }
        div[data-baseweb="select"] * {
            color: black !important;
        }
        div[data-baseweb="select"] > div {
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

# Navigation: "User" and "Admin" modes only.
mode = st.sidebar.selectbox("Select Mode", ["User", "Admin"])

if mode == "User":
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
                    # --- Greeting & Basic Info Section (Card Design) ---
                    basic_info = result.get("basic_info", {})
                    if basic_info.get("name"):
                        st.markdown(f"<h2 style='color:#15967D;'>Hello, {basic_info.get('name')}!</h2>", unsafe_allow_html=True)
                    
                    st.markdown("<div style='background-color:#15967D; padding:10px; border-radius:5px; display:inline-block; margin-bottom:10px;'>"
                                "<h3 style='color:white;'>Basic Info</h3></div>", unsafe_allow_html=True)
                    st.markdown(f"""
                    <div style='background-color:#F5F5F5; padding:15px; border-radius:5px; margin-bottom:20px;'>
                        <strong>Name:</strong> {basic_info.get('name', 'N/A')}<br>
                        <strong>Email:</strong> {basic_info.get('email', 'N/A')}<br>
                        <strong>Mobile:</strong> {basic_info.get('mobile', 'N/A')}<br>
                        <strong>Address:</strong> {basic_info.get('address', 'N/A')}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # --- AI Resume Summary Section ---
                    st.markdown("<div style='background-color:#15967D; padding:10px; border-radius:5px; display:inline-block; margin-bottom:10px;'>"
                                "<h3 style='color:white;'>AI Resume Summary</h3></div>", unsafe_allow_html=True)
                    st.markdown("<p style='font-size:16px; font-style:italic; color:#555555;'>A concise summary of your experience, skills, and expertise, tailored for ATS optimization. This summary gives hiring managers a quick overview of your professional profile.</p>", unsafe_allow_html=True)
                    st.markdown(f"""
                    <div style='background-color:#F5F5F5; padding:15px; border-left: 4px solid #15967D; border-radius:3px; margin-bottom:20px;'>
                        {result.get('ai_resume_summary', '')}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # --- Resume Score Section (Simple) ---
                    st.markdown("<h3 style='color:#15967D;'>Resume Score</h3>", unsafe_allow_html=True)
                    resume_score_raw = result.get("resume_score", "70/100")
                    if isinstance(resume_score_raw, int):
                        resume_score = resume_score_raw
                    elif isinstance(resume_score_raw, str):
                        resume_score_match = re.search(r'\d+', resume_score_raw)
                        resume_score = int(resume_score_match.group()) if resume_score_match else 70
                    else:
                        resume_score = 70
                    st.metric(label="Score", value=f"{resume_score}/100")
                    st.markdown("<p style='font-size:14px; color:#555555;'><em>Note: The score is derived from structure, keyword usage, clarity, and overall presentation.</em></p>", unsafe_allow_html=True)
                    
                    # --- Skills Section (Plain Headings) ---
                    st.markdown("<h3 style='color:#15967D;'>Skills</h3>", unsafe_allow_html=True)
                    st.markdown("<h4 style='color:#15967D;'>Current Skills</h4>", unsafe_allow_html=True)
                    for skill in result.get("skills", {}).get("current_skills", []):
                        st.markdown(f"- {skill}")
                    st.markdown("<h4 style='color:#15967D;'>Recommended Skills</h4>", unsafe_allow_html=True)
                    for skill in result.get("skills", {}).get("recommended_skills", []):
                        st.markdown(f"- {skill}")
                    
                    # --- Recommended Courses Section (Plain Container) ---
                    st.markdown("<h3 style='color:#15967D;'>Recommended Courses</h3>", unsafe_allow_html=True)
                    st.write("Courses suggested to help you enhance your skillset:")
                    for course in result.get("course_recommendations", []):
                        if isinstance(course, dict):
                            platform = course.get("platform", "Unknown Platform")
                            course_name = course.get("course_name", "Unknown Course")
                            link = course.get("link", "#")
                            st.markdown(f"- <span style='color:#15967D; font-weight:bold;'>{platform}</span>: [{course_name}]({link})", unsafe_allow_html=True)
                        else:
                            st.markdown(f"- {course}")
                    
                    # --- Appreciation Section ---
                    st.markdown("<h3 style='color:#15967D;'>Appreciation</h3>", unsafe_allow_html=True)
                    st.write("Positive comments acknowledging your strengths:")
                    for comment in result.get("appreciation", []):
                        st.markdown(f"- {comment}")
                    
                    # --- Resume Tips Section ---
                    st.markdown("<h3 style='color:#15967D;'>Resume Tips</h3>", unsafe_allow_html=True)
                    st.write("Constructive suggestions for improving your resume:")
                    for tip in result.get("resume_tips", []):
                        st.markdown(f"- {tip}")
                    
                    # --- Matching Job Roles Section ---
                    st.markdown("<h3 style='color:#15967D;'>Matching Job Roles</h3>", unsafe_allow_html=True)
                    st.write("Job roles that match your skills and experience:")
                    for role in result.get("matching_job_roles", []):
                        st.markdown(f"- {role}")
                    
                    # --- ATS Keywords Section ---
                    st.markdown("<h3 style='color:#15967D;'>ATS Keywords</h3>", unsafe_allow_html=True)
                    st.write("Industry-relevant keywords for better ATS performance. These keywords help your resume get noticed by automated systems and recruiters alike.")
                    ats_keywords = result.get("ats_keywords", [])
                    if isinstance(ats_keywords, list):
                        for keyword in ats_keywords:
                            st.markdown(f"- {keyword}")
                    else:
                        st.json(ats_keywords)
                    
                    # --- Project Suggestions Section ---
                    st.markdown("<h3 style='color:#15967D;'>Project Suggestions</h3>", unsafe_allow_html=True)
                    with st.expander("Improvement Tips for Existing Projects", expanded=True):
                        for tip in result.get("project_suggestions", {}).get("improvement_tips", []):
                            st.markdown(f"- {tip}")
                    with st.expander("New Project Recommendations", expanded=True):
                        for proj in result.get("project_suggestions", {}).get("new_project_recommendations", []):
                            st.markdown(f"- {proj}")
                    
                    # --- Resume Writing Tips Section ---
                    st.markdown("<h3 style='color:#15967D;'>Resume Writing Tips</h3>", unsafe_allow_html=True)
                    st.write("Check out these high-rated YouTube videos for expert resume writing tips:")
                    col_video1, col_video2 = st.columns(2)
                    with col_video1:
                        st.video("https://youtu.be/Tt08KmFfIYQ?si=mU-0_Mcoq8SO_2qt")
                    with col_video2:
                        st.video("https://youtu.be/aD7fP-2u3iY?si=KPnyC0D7HRStOWpB")
                    
                    # --- Export Results Section ---
                    st.markdown("<h3 style='color:#15967D;'>Export Your Details</h3>", unsafe_allow_html=True)
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

# --- Admin Panel Code ---
if mode == "Admin":
    st.title("🔐 Admin Dashboard")
    
    # Store login state in session_state
    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False

    if not st.session_state.admin_logged_in:
        admin_user = st.text_input("Username")
        admin_pass = st.text_input("Password", type="password")
        if st.button("Login"):
            if admin_user == st.secrets["user_name"] and admin_pass == st.secrets["pass"]:
                st.session_state.admin_logged_in = True
                st.success("Logged in as Admin")
                st.rerun()
            else:
                st.error("Invalid Admin Credentials")

    if st.session_state.admin_logged_in:
        # Fetch data from database
        cursor.execute("SELECT * FROM user_data")
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=['ID', 'Name', 'Email', 'Resume_Score', 'Skills', 'Recommended_Skills', 'Courses', 'Timestamp'])
        
        st.markdown("<h3 style='color:#15967D;'>User Data</h3>", unsafe_allow_html=True)
        st.dataframe(df)
        
        st.markdown("<h3 style='color:#15967D;'>Resume Score Distribution</h3>", unsafe_allow_html=True)
        st.bar_chart(df['Resume_Score'])
        
        st.markdown("<h3 style='color:#15967D;'>Top Skills Overview</h3>", unsafe_allow_html=True)
        def get_top_skills(skill_series, top_n=5):
            skill_counts = pd.Series(", ".join(skill_series).split(", ")).value_counts()
            if len(skill_counts) > top_n:
                top_skills = skill_counts.head(top_n)
                top_skills.loc["Others"] = skill_counts[top_n:].sum()
            else:
                top_skills = skill_counts
            return top_skills

        top_current_skills = get_top_skills(df['Skills'])
        top_recommended_skills = get_top_skills(df['Recommended_Skills'])

        # Create common figure with increased size and reduced gap
        fig, axes = plt.subplots(1, 2, figsize=(20, 12))
        plt.subplots_adjust(wspace=0.3)
        def plot_pie(ax, data, title):
            data.plot.pie(ax=ax, autopct='%1.1f%%', startangle=140, wedgeprops={'edgecolor':'white'}, legend=False)
            ax.set_ylabel('')
            ax.set_title(title)
        plot_pie(axes[0], top_current_skills, "Current Skills")
        plot_pie(axes[1], top_recommended_skills, "Recommended Skills")
        st.pyplot(fig)
        
        # Manage Data Section: Export and Clear Buttons
        st.markdown("<h3 style='color:#15967D;'>Manage Data</h3>", unsafe_allow_html=True)
        col1, col_gap, col2 = st.columns([1, 0.5, 1])
        with col1:
            export_json = df.to_json(orient="records", indent=4)
            st.download_button("Download All Data as JSON", data=export_json, file_name="user_data.json", mime="application/json")
        with col2:
            if st.button("Clear Results", key="clear_admin"):
                cursor.execute("DELETE FROM user_data")
                conn.commit()
                st.success("All results have been cleared from the database.")
                st.rerun()  # Forces an immediate refresh

        # Update Database Feature: Upload JSON file to update data
        st.markdown("<h3 style='color:#15967D;'>Update Database</h3>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload JSON File to Update Database", type=["json"], key="update_json")
        if uploaded_file is not None:
            try:
                new_data = json.load(uploaded_file)
                if isinstance(new_data, list):
                    for record in new_data:
                        # Map JSON keys (with spaces) to DB columns (without spaces)
                        rec_id = record.get("ID")
                        name = record.get("Name")
                        email = record.get("Email")
                        resume_score = record.get("Resume Score")
                        skills = record.get("Skills")
                        rec_skills = record.get("Recommended Skills")
                        courses = record.get("Courses")
                        timestamp = record.get("Timestamp")
                        cursor.execute("""
                            INSERT OR REPLACE INTO user_data (id, name, email, resume_score, skills, recommended_skills, courses, timestamp)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (rec_id, name, email, resume_score, skills, rec_skills, courses, timestamp))
                    conn.commit()
                    st.success("Database successfully updated!")
                    st.rerun()  # Force refresh to show updated data
                else:
                    st.error("Invalid JSON format. Please upload a valid JSON file.")
            except Exception as e:
                st.error(f"Error processing JSON file: {e}")

