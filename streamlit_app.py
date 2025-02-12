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

# ------------------------
# Helper Functions
# ------------------------

def extract_json(response_text):
    """
    Extracts JSON from a string using regex.
    Returns a dictionary if valid JSON is found, else an empty dictionary.
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
    Returns True if valid, else False.
    """
    keywords = ["education", "experience", "skills", "projects", "certifications"]
    return any(keyword in text.lower() for keyword in keywords)

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
# API Configuration and Resume Analysis
# ------------------------
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = st.secrets["API_KEY"]  # Securely access the API key

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
st.set_page_config(page_title="NextGen Resume Analyzer", page_icon="📄")
st.sidebar.title("User Mode")

# Sidebar styling
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            background-color: #15967D !important; /* Darker Teal */
            color: white !important;
        }
        [data-testid="stSidebar"] * {
            color: white !important;
        }
        /* Fix select box text color */
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

mode = st.sidebar.selectbox("Select Mode", ["User", "Admin"])

if mode == "User":
    st.title("📄 NextGen Resume Analyzer")
    uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"])
    if uploaded_file:
        st.success("File uploaded successfully!")
        resume_text = extract_text_from_pdf(uploaded_file)
        st.markdown("Click the <span style='color: #15967D; font-weight: bold;'>Analyze Resume</span> button to proceed.", unsafe_allow_html=True)
        
        if not validate_resume(resume_text):
            st.error("❌ The uploaded document does not appear to be a valid resume. Please upload a proper resume file.")
        else:
            if st.button("Analyze Resume"):
                with st.spinner("Analyzing resume..."):
                    result = get_resume_analysis(resume_text)
                if "error" in result:
                    st.error(result["error"])
                else:
                    # --- Greeting & Basic Info Section ---
                    basic_info = result.get("basic_info", {})
                    if basic_info.get("name"):
                        st.markdown(f"<h2>Hello, {basic_info.get('name')}!</h2>", unsafe_allow_html=True)
                    
                    st.markdown("<h3>Basic Info</h3>", unsafe_allow_html=True)
                    st.markdown(f"""
                    <div style='background-color:#F0F0F0; padding:10px; border-radius:5px;'>
                        <strong>Name:</strong> {basic_info.get('name', 'N/A')}<br>
                        <strong>Email:</strong> {basic_info.get('email', 'N/A')}<br>
                        <strong>Mobile:</strong> {basic_info.get('mobile', 'N/A')}<br>
                        <strong>Address:</strong> {basic_info.get('address', 'N/A')}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # --- AI Resume Summary Section ---
                    st.markdown("<h3>AI Resume Summary</h3>", unsafe_allow_html=True)
                    st.markdown("<p style='font-size:16px; line-height:1.5; color:#333333;'>A concise summary of your experience, skills, and expertise, tailored for ATS optimization.</p>", unsafe_allow_html=True)
                    st.markdown(f"""
                    <div style='background-color:#F9F9F9; padding:10px; border-left: 4px solid #15967D; border-radius:3px;'>
                        {result.get('ai_resume_summary', '')}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # --- Resume Score Section ---
                    st.header("Resume Score")
                    resume_score_raw = result.get("resume_score", "70/100")
                    if isinstance(resume_score_raw, int):
                        resume_score = resume_score_raw
                    elif isinstance(resume_score_raw, str):
                        resume_score_match = re.search(r'\d+', resume_score_raw)
                        resume_score = int(resume_score_match.group()) if resume_score_match else 70
                    else:
                        resume_score = 70
                    st.metric(label="Score", value=f"{resume_score}/100")
                    st.markdown("**Note:** The score is derived from an evaluation of structure, keyword usage, clarity, and overall presentation.")
                    
                    # --- Skills Section with Differentiated Design ---
                    st.header("Skills")
                    col_skills1, col_skills2 = st.columns(2)
                    with col_skills1:
                        st.markdown("<h4 style='color:#15967D;'>Current Skills</h4>", unsafe_allow_html=True)
                        for skill in result.get("skills", {}).get("current_skills", []):
                            st.markdown(f"- {skill}")
                    with col_skills2:
                        st.markdown("<h4 style='color:#15967D;'>Recommended Skills</h4>", unsafe_allow_html=True)
                        for skill in result.get("skills", {}).get("recommended_skills", []):
                            st.markdown(f"- {skill}")
                    
                    # --- Recommended Courses Section with Slider ---
                    st.header("Recommended Courses")
                    num_courses = st.slider("Select number of course recommendations to display:", min_value=1, max_value=10, value=5)
                    st.write("Courses suggested to help you enhance your skillset and improve your resume:")
                    for course in result.get("course_recommendations", [])[:num_courses]:
                        if isinstance(course, dict):
                            platform = course.get("platform", "Unknown Platform")
                            course_name = course.get("course_name", "Unknown Course")
                            link = course.get("link", "#")
                            st.markdown(f"- <span style='color:#15967D; font-weight:bold;'>{platform}</span>: [{course_name}]({link})", unsafe_allow_html=True)
                        else:
                            st.markdown(f"- {course}")
                    
                    # --- Appreciation Section ---
                    st.header("Appreciation")
                    st.write("Here are some positive comments acknowledging your strengths in the resume:")
                    for comment in result.get("appreciation", []):
                        st.markdown(f"- {comment}")
                    
                    # --- Resume Tips Section ---
                    st.header("Resume Tips")
                    st.write("Constructive suggestions for improving your resume:")
                    for tip in result.get("resume_tips", []):
                        st.markdown(f"- {tip}")
                    
                    # --- Matching Job Roles Section ---
                    st.header("Matching Job Roles")
                    st.write("Job roles that match your skills and experience:")
                    for role in result.get("matching_job_roles", []):
                        st.markdown(f"- {role}")
                    
                    # --- ATS Keywords Section ---
                    st.header("ATS Keywords")
                    st.write("Industry-relevant keywords that can improve your resume's performance in Applicant Tracking Systems (ATS):")
                    ats_keywords = result.get("ats_keywords", [])
                    if isinstance(ats_keywords, list):
                        for keyword in ats_keywords:
                            st.markdown(f"- {keyword}")
                    else:
                        st.json(ats_keywords)
                    
                    # --- Project Suggestions Section with Expanders and Color Styling ---
                    st.header("Project Suggestions")
                    with st.expander("Improvement Tips for Existing Projects", expanded=True):
                        for tip in result.get("project_suggestions", {}).get("improvement_tips", []):
                            st.markdown(f"- {tip}")
                    with st.expander("New Project Recommendations", expanded=True):
                        for proj in result.get("project_suggestions", {}).get("new_project_recommendations", []):
                            st.markdown(f"- {proj}")
                    
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

elif mode == "Admin":
    st.title("🔐 Admin Dashboard")
    admin_user = st.text_input("Username")
    admin_pass = st.text_input("Password", type="password")
    if st.button("Login"):
        if admin_user == st.secrets["user_name"] and admin_pass == st.secrets["pass"]:
            st.success("Logged in as Admin")
        
            cursor.execute("SELECT * FROM user_data")
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=['ID', 'Name', 'Email', 'Resume Score', 'Skills', 'Recommended Skills', 'Courses', 'Timestamp'])
        
            st.header("User Data")
            st.dataframe(df)
        
            # Resume Score Chart
            st.subheader("Resume Score Distribution")
            st.bar_chart(df['Resume Score'])
        
            # Top Skills Chart
            st.subheader("Top Skills Overview")
            
            def get_top_skills(skill_series, top_n=5):
                skill_counts = pd.Series(", ".join(skill_series).split(", ")).value_counts()
                if len(skill_counts) > top_n:
                    top_skills = skill_counts.head(top_n)
                    top_skills.loc["Others"] = skill_counts[top_n:].sum()  # Group remaining skills as "Others"
                else:
                    top_skills = skill_counts
                return top_skills
            
            top_current_skills = get_top_skills(df['Skills'])
            top_recommended_skills = get_top_skills(df['Recommended Skills'])
            
            # Use side-by-side columns for charts
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
