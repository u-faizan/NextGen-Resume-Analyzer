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
    """
    Extracts JSON from a string using regex.
    """
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
    """
    Checks if the extracted text contains common resume keywords.
    """
    keywords = ["education", "experience", "skills", "projects", "certifications"]
    return any(keyword in text.lower() for keyword in keywords)

def get_top_skills(skill_series, top_n=5):
    """
    Groups and counts skills from a Series, filtering out empty values and
    grouping extras under 'Others'.
    """
    # Clean the series: remove NaNs and empty strings
    cleaned = [str(skill) for skill in skill_series if pd.notna(skill) and str(skill).strip()]
    if not cleaned:
        return pd.Series(dtype=int)
    # Join the cleaned strings and split by comma
    skills_list = ", ".join(cleaned).split(", ")
    counts = pd.Series(skills_list).value_counts()
    if len(counts) > top_n:
        top_skills = counts.head(top_n)
        top_skills["Others"] = counts.iloc[top_n:].sum()
        return top_skills
    return counts

# ===========================
# Database Setup
# ===========================
# Connect to (or create) the SQLite database
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
        timestamp TEXT,
        feedback TEXT
    )
''')
conn.commit()


# ===========================
# API Configuration & Resume Analysis
# ===========================
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = st.secrets["API_KEY"]

def get_resume_analysis(resume_text):
    """
    Sends resume text to the API and returns the analysis result.
    """
    prompt = f"""
You are an expert resume analyzer. You must produce valid JSON output and ensure all URLs are valid and relevant to the recommended courses. Additionally, you must tailor job roles to the candidate’s experience level. For example, if the resume indicates an entry-level or student background, include junior- or intern-level job roles (e.g., 'Data Science Intern', 'Junior Data Scientist', 'Machine Learning Intern') rather than exclusively senior positions.

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
        "link": valid URL (ensure this is an active, relevant course URL)
    }},
    "appreciation": list of at least 5 personalized positive comments,
    "resume_tips": list of at least 5 suggestions for improvement,
    "resume_score": string (score in "XX/100" format),
    "ai_resume_summary": string (a concise summary for ATS optimization),
    "matching_job_roles": list of 2-3 job roles specifically relevant to the candidate’s experience level,
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
    """
    Saves an uploaded PDF to disk temporarily and extracts text from it.
    """
    if uploaded_file is not None:
        with open("temp_resume.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())
        return extract_text("temp_resume.pdf")
    else:
        return ""

# ===========================
# Main App Layout and Branding
# ===========================
# Header with Branding
st.markdown("""
<div style="background-color:#15967D; padding:20px; text-align:left; border-bottom: 3px solid #15967D;">
    <span style="font-size: 2.5em; font-weight: bold; color:white;"> 📝 NextGen Resume Analyzer</span>
</div>
""", unsafe_allow_html=True)

# Sidebar styling and mode selection
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

# Navigation between User and Admin modes
mode = st.sidebar.selectbox("Select Mode", ["User", "Admin"])

# ===========================
# Sidebar: About / How-to / Contact
# ===========================
st.sidebar.markdown(
    """
    <style>
    /* Styling for prominent headings using a darker shade */
    .sidebar-heading {
        background-color: #117864; /* Darker shade than the main teal */
        color: white;
        padding: 5px 10px;
        border-radius: 4px;
        font-size: 1.2em;
        font-weight: bold;
        margin-bottom: 5px;
        margin-left: -10px; /* Shift heading slightly left */
        width: calc(100% + 10px);
    }
    /* Styling for body text: flush left with no extra left padding */
    .sidebar-body {
        margin: 0;
        padding-left: 0;
        padding-right: 0;
        line-height: 1.4;
    }
    </style>
    
    <div class="sidebar-heading">About This App</div>
    <p class="sidebar-body">
        NextGen Resume Analyzer is a powerful tool to help you analyze your resume's structure, keyword optimization, and overall effectiveness. Gain insights into how your resume performs against Applicant Tracking Systems (ATS) and discover personalized tips for improvement.
    </p>
    
    <br>
    <div class="sidebar-heading">How to Use This App</div>
    <p class="sidebar-body">
        1. <strong>Upload</strong> your resume (PDF format) using the "Upload Your Resume" widget.<br>
        2. <strong>Click</strong> the "Analyze Resume" button after a successful upload.<br>
        3. <strong>Wait</strong> a few seconds for the analysis to complete.<br>
        4. <strong>Explore</strong> your personalized resume feedback, tips, and recommendations!
    </p>
    
    <br>
    <div class="sidebar-heading">About the Developer</div>
    <p class="sidebar-body">
        Developed by <strong>Umar Faizan</strong><br>
        <strong>Email:</strong> <a href="mailto:mianumarzareen@gmail.com">mianumarzareen@gmail.com</a><br>
        <strong>GitHub Repo:</strong> <a href="https://github.com/u-faizan/NextGen-Resume-Analyzer" target="_blank">NextGen-Resume-Analyzer</a><br>
        Feel free to reach out for any questions, feedback, or collaborations!
    </p>
    """,
    unsafe_allow_html=True
)


# ===========================
# User Mode
# ===========================
if mode == "User":
    st.title("User Dashboard")

    # Check if an analysis result already exists in session state
    if "analysis_result" not in st.session_state:
        # File uploader for resume (PDF)
        uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"])
    else:
        # If analysis was already performed, no need to show uploader
        uploaded_file = None

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
                    # Store analysis result in session state to prevent loss on rerun
                    st.session_state.analysis_result = result

    if "analysis_result" in st.session_state:
        result = st.session_state.analysis_result

        # --- Greeting & Basic Info Section ---
        basic_info = result.get("basic_info", {})
        # Use "Null" as placeholder if missing
        name = basic_info.get("name", "Null")
        email = basic_info.get("email", "Null")
        mobile = basic_info.get("mobile", "Null")
        address = basic_info.get("address", "Null")
        
        if name != "Null":
            st.markdown(f"<h2 style='color:#15967D;'>Hello, {name}!</h2>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background-color:#15967D; padding:10px; border-radius:5px; display:inline-block; margin-bottom:10px;">
            <h3 style="color:white; margin:0;">Basic Info</h3>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background-color:#F5F5F5; padding:15px; border-radius:5px; margin-bottom:20px;">
            <strong>Name:</strong> {name}<br>
            <strong>Email:</strong> {email}<br>
            <strong>Mobile:</strong> {mobile}<br>
            <strong>Address:</strong> {address}
        </div>
        """, unsafe_allow_html=True)
        
        # --- AI Resume Summary Section ---
        st.markdown("""
        <div style="background-color:#15967D; padding:10px; border-radius:5px; display:inline-block; margin-bottom:10px;">
            <h3 style="color:white; margin:0;">AI Resume Summary</h3>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<p style='font-size:16px; font-style:italic; color:#555555;'>A concise summary of your experience, skills, and expertise, tailored for ATS optimization. This summary provides a quick overview for hiring managers.</p>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background-color:#F5F5F5; padding:15px; border-left: 4px solid #15967D; border-radius:3px; margin-bottom:20px;">
            {result.get('ai_resume_summary', 'Null')}
        </div>
        """, unsafe_allow_html=True)
        
        # --- Resume Score Section ---
        st.markdown("""
        <div style="background-color:#15967D; padding:10px; border-radius:5px; display:inline-block; margin-bottom:10px;">
            <h3 style="color:white; margin:0;">Resume Score</h3>
        </div>
        """, unsafe_allow_html=True)
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
        
        # --- Skills Section with Side-by-Side Layout ---
        st.markdown("""
        <div style="background-color:#15967D; padding:10px; border-radius:5px; display:inline-block; margin-bottom:10px;">
            <h3 style="color:white; margin:0;">Skills</h3>
        </div>
        """, unsafe_allow_html=True)
        col_skills1, col_skills2 = st.columns(2)
        with col_skills1:
            st.markdown("<div style='background-color:#EFEFEF; padding:10px; border-radius:5px;'><h4 style='color:#15967D;'>Current Skills</h4></div>", unsafe_allow_html=True)
            for skill in result.get("skills", {}).get("current_skills", []):
                st.markdown(f"- {skill}")
        with col_skills2:
            st.markdown("<div style='background-color:#EFEFEF; padding:10px; border-radius:5px;'><h4 style='color:#15967D;'>Recommended Skills</h4></div>", unsafe_allow_html=True)
            for skill in result.get("skills", {}).get("recommended_skills", []):
                st.markdown(f"- {skill}")
        
        # --- Recommended Courses Section ---
        st.markdown("""
        <div style="background-color:#15967D; padding:10px; border-radius:5px; display:inline-block; margin-bottom:10px;">
            <h3 style="color:white; margin:0;">Recommended Courses</h3>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<p style='font-size:16px; font-style:italic; color:#555555;'>Courses suggested to help you enhance your skillset:</p>", unsafe_allow_html=True)
        for course in result.get("course_recommendations", []):
            if isinstance(course, dict):
                platform = course.get("platform", "Unknown Platform")
                course_name = course.get("course_name", "Unknown Course")
                link = course.get("link", "#")
                st.markdown(f"- <span style='color:#15967D; font-weight:bold;'>{platform}</span>: [{course_name}]({link})", unsafe_allow_html=True)
            else:
                st.markdown(f"- {course}")
        
        # --- Appreciation Section ---
        st.markdown("""
        <div style="background-color:#15967D; padding:10px; border-radius:5px; display:inline-block; margin-bottom:10px;">
            <h3 style="color:white; margin:0;">Appreciation</h3>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<p style='font-size:16px; font-style:italic; color:#555555;'>Positive comments acknowledging your strengths</p>", unsafe_allow_html=True)
        for comment in result.get("appreciation", []):
            st.markdown(f"- {comment}")
        
        # --- Resume Tips Section ---
        st.markdown("""
        <div style="background-color:#15967D; padding:10px; border-radius:5px; display:inline-block; margin-bottom:10px;">
            <h3 style="color:white; margin:0;">Resume Tips</h3>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<p style='font-size:16px; font-style:italic; color:#555555;'>Constructive suggestions for improving your resume:</p>", unsafe_allow_html=True)
        for tip in result.get("resume_tips", []):
            st.markdown(f"- {tip}")
        
        # --- Matching Job Roles Section ---
        st.markdown("""
        <div style="background-color:#15967D; padding:10px; border-radius:5px; display:inline-block; margin-bottom:10px;">
            <h3 style="color:white; margin:0;">Matching Job Roles</h3>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<p style='font-size:16px; font-style:italic; color:#555555;'>Job roles that match your skills and experience:</p>", unsafe_allow_html=True)
        for role in result.get("matching_job_roles", []):
            st.markdown(f"- {role}")
        
        # --- ATS Keywords Section ---
        st.markdown("""
        <div style="background-color:#15967D; padding:10px; border-radius:5px; display:inline-block; margin-bottom:10px;">
            <h3 style="color:white; margin:0;">ATS Keywords</h3>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<p style='font-size:16px; font-style:italic; color:#555555;'>Industry-relevant keywords for better ATS performance:</p>", unsafe_allow_html=True)
        ats_keywords = result.get("ats_keywords", [])
        if isinstance(ats_keywords, list):
            for keyword in ats_keywords:
                st.markdown(f"- {keyword}")
        else:
            st.json(ats_keywords)
        
        # --- Project Suggestions Section ---
        st.markdown("""
        <div style="background-color:#15967D; padding:10px; border-radius:5px; display:inline-block; margin-bottom:10px;">
            <h3 style="color:white; margin:0;">Project Suggestions</h3>
        </div>
        """, unsafe_allow_html=True)
        with st.expander("Improvement Tips for Existing Projects", expanded=True):
            for tip in result.get("project_suggestions", {}).get("improvement_tips", []):
                st.markdown(f"- {tip}")
        with st.expander("New Project Recommendations", expanded=True):
            for proj in result.get("project_suggestions", {}).get("new_project_recommendations", []):
                st.markdown(f"- {proj}")
        
        # --- Resume Writing Tips Section ---
        st.markdown("""
        <div style="background-color:#15967D; padding:10px; border-radius:5px; display:inline-block; margin-bottom:10px;">
            <h3 style="color:white; margin:0;">Resume Writing Tips</h3>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<p style='font-size:16px; font-style:italic; color:#555555;'>Check out these high-rated YouTube videos for expert resume writing tips:</p>", unsafe_allow_html=True)
        col_video1, col_video2 = st.columns(2)
        with col_video1:
            st.video("https://youtu.be/Tt08KmFfIYQ?si=mU-0_Mcoq8SO_2qt")
        with col_video2:
            st.video("https://youtu.be/aD7fP-2u3iY?si=KPnyC0D7HRStOWpB")
        

        # --- Automatically Save Analysis Record if Not Already Saved ---
        if "record_saved" not in st.session_state:
            cursor.execute('''
                INSERT INTO user_data (name, email, resume_score, skills, recommended_skills, courses, feedback, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            ''', (
                name,
                email,
                resume_score,
                ", ".join(result.get("skills", {}).get("current_skills", [])),
                ", ".join(result.get("skills", {}).get("recommended_skills", [])),
                ", ".join([course.get("course_name", "Null") if isinstance(course, dict) else str(course)
                           for course in result.get("course_recommendations", [])]),
                ""  # Feedback is initially empty
            ))
            conn.commit()
            st.session_state.record_saved = True
            st.session_state.record_id = cursor.lastrowid
        
        # --- Feedback Section (Always Shown) ---
        # Initialize the feedback submission flag if not already set.
        if "feedback_submitted" not in st.session_state:
            st.session_state.feedback_submitted = False
        
        st.markdown("""
        <div style="background-color:#15967D; padding:10px; border-radius:5px; display:inline-block; margin-bottom:10px;">
            <h3 style="color:white; margin:0;">Feedback</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.feedback_submitted:
            feedback_input = st.text_area("Please provide your feedback (optional):", "")
            if st.button("Submit Feedback"):
                # Update the saved record with the new feedback.
                cursor.execute("UPDATE user_data SET feedback=? WHERE id=?", (feedback_input, st.session_state.record_id))
                conn.commit()
                st.session_state.feedback_submitted = True
                st.session_state.final_feedback = feedback_input
                st.success("Feedback submitted! Thank you.")
        else:
            st.info("You have already submitted your feedback. Thank you!")
        
        # Ensure final_feedback exists for export (defaults to an empty string).
        if "final_feedback" not in st.session_state:
            st.session_state.final_feedback = ""
        final_feedback = st.session_state.final_feedback


        
        # --- Export Results Section (Single Instance) ---
        st.markdown("<h3 style='color:#15967D;'>Export Your Details</h3>", unsafe_allow_html=True)
        export_data = {
            "Basic Info": {
                "name": name,
                "email": email,
                "mobile": mobile,
                "address": address
            },
            "AI Resume Summary": result.get("ai_resume_summary", "Null"),
            "Resume Score": resume_score,
            "Skills": result.get("skills", {}),
            "Recommended Courses": result.get("course_recommendations", []),
            "Appreciation": result.get("appreciation", []),
            "Resume Tips": result.get("resume_tips", []),
            "Matching Job Roles": result.get("matching_job_roles", []),
            "ATS Keywords": result.get("ats_keywords", []),
            "Project Suggestions": result.get("project_suggestions", {}),
            "Feedback": final_feedback
        }
        export_json = json.dumps(export_data, indent=4)
        st.download_button("Download Details as JSON", data=export_json, file_name="resume_analysis.json", mime="application/json")

# ===========================
# Admin Mode
# ===========================
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
        # Helper function to load data from the database into a DataFrame
        def load_data():
            cursor.execute("SELECT * FROM user_data")
            data = cursor.fetchall()
            # Updated columns list includes "Feedback"
            return pd.DataFrame(
                data,
                columns=['ID', 'Name', 'Email', 'Resume_Score', 'Skills', 'Recommended_Skills', 'Courses', 'Timestamp','Feedback']
            )
        
        # 1) Load the data initially
        df = load_data()
        
        # 2) Clear data if the button is clicked
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
                df = load_data()

        # 3) Now display the data (which might be empty if just cleared)
        st.markdown("<h3 style='color:#15967D;'>User Data</h3>", unsafe_allow_html=True)
        st.dataframe(df)

        # 4) Resume Score Distribution
        st.markdown("<h3 style='color:#15967D;'>Resume Score Distribution</h3>", unsafe_allow_html=True)
        if df.empty:
            st.info("No data available.")
        else:
            st.bar_chart(df['Resume_Score'])
        
        # 5) Top Skills Overview
        st.markdown("<h3 style='color:#15967D;'>Top Skills Overview</h3>", unsafe_allow_html=True)
        def get_top_skills(skill_series, top_n=5):
            skills = [str(s).strip() for s in skill_series if pd.notna(s) and str(s).strip() != ""]
            if not skills:
                return pd.Series(dtype=int)
            skill_counts = pd.Series(", ".join(skills).split(", ")).value_counts()
            if len(skill_counts) > top_n:
                top_skills = skill_counts.head(top_n)
                top_skills.loc["Others"] = skill_counts[top_n:].sum()
            else:
                top_skills = skill_counts
            return top_skills

        if df.empty:
            st.info("No data available.")
        else:
            top_current_skills = get_top_skills(df['Skills'])
            top_recommended_skills = get_top_skills(df['Recommended_Skills'])
            
            fig, axes = plt.subplots(1, 2, figsize=(20, 12))
            plt.subplots_adjust(wspace=0.3)

            def plot_pie(ax, data, title):
                data.plot.pie(
                    ax=ax, autopct='%1.1f%%', startangle=140,
                    wedgeprops={'edgecolor': 'white'}, legend=False
                )
                ax.set_ylabel('')
                ax.set_title(title)

            if not top_current_skills.empty:
                plot_pie(axes[0], top_current_skills, "Current Skills")
            else:
                axes[0].text(0.5, 0.5, "No Data", ha='center', va='center')

            if not top_recommended_skills.empty:
                plot_pie(axes[1], top_recommended_skills, "Recommended Skills")
            else:
                axes[1].text(0.5, 0.5, "No Data", ha='center', va='center')

            st.pyplot(fig)
