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
    "course_recommendations": list of at least 5 courses with details as:
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
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            background-color: #15967D !important; /* Darker Teal */
            color: white !important;
        }
        [data-testid="stSidebar"] * {
            color: white !important; /* Sidebar text color */
        }
    </style>
    """,
    unsafe_allow_html=True
)


mode = st.sidebar.selectbox("Select Mode", ["User", "Admin"])

if mode == "User":
    st.title("📄 Smart Resume Analyzer")
    uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"])
    if uploaded_file:
        st.success("File uploaded successfully!")
        resume_text = extract_text_from_pdf(uploaded_file)
        st.subheader("Extracted Resume Preview")
        st.text(resume_text[:500] + "...")
        st.subheader("Click the 'Analyze Resume' button to proceed")
    
        
        if not validate_resume(resume_text):
            st.error("❌ The uploaded document does not appear to be a valid resume. Please upload a proper resume file.")
        else:
            if st.button("Analyze Resume"):
                with st.spinner("Analyzing resume..."):
                    result = get_resume_analysis(resume_text)
                if "error" in result:
                    st.error(result["error"])
                else:
                    # Extract values from the result
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
                    
                    # Display the results with descriptions
                    st.header("Basic Info")
                    st.write("This section displays your personal details extracted from your resume (Name, Email, Mobile, Address).")
                    st.json(basic_info)
                    
                    st.header("AI Resume Summary")
                    st.write("A concise summary of your experience, skills, and expertise, tailored for ATS optimization.")
                    st.write(result.get("ai_resume_summary", ""))
                    
                    st.header("Resume Score")
                    st.write("Your resume is scored based on formatting, ATS optimization, content quality, readability, and relevance.")
                    st.metric(label="Score", value=f"{resume_score}/100")
                    st.markdown("**Note:** The score is derived from an evaluation of structure, keyword usage, clarity, and overall presentation.")
                    
                    st.header("Skills")
                    st.subheader("Current Skills")
                    st.write("These are the skills currently listed in your resume:")
                    for skill in skills.get("current_skills", []):
                        st.markdown(f"- {skill}")
                    
                    st.subheader("Recommended Skills")
                    st.write("These skills are recommended for you to improve your resume:")
                    for skill in skills.get("recommended_skills", []):
                        st.markdown(f"- {skill}")
                    
                    st.header("Recommended Courses")
                    st.write("Courses suggested to help you enhance your skillset and improve your resume:")
                    for course in course_recommendations:
                        if isinstance(course, dict):
                            platform = course.get("platform", "Unknown Platform")
                            course_name = course.get("course_name", "Unknown Course")
                            link = course.get("link", "#")
                            st.markdown(f"- **{platform}**: [{course_name}]({link})")
                        else:
                            st.markdown(f"- {course}")
                    
                    st.header("Appreciation")
                    st.write("Here are some positive comments acknowledging your strengths in the resume:")
                    for comment in result.get("appreciation", []):
                        st.markdown(f"- {comment}")
                    
                    st.header("Resume Tips")
                    st.write("Constructive suggestions for improving your resume:")
                    for tip in result.get("resume_tips", []):
                        st.markdown(f"- {tip}")
                    
                    st.header("Matching Job Roles")
                    st.write("Job roles that match your skills and experience:")
                    for role in result.get("matching_job_roles", []):
                        st.markdown(f"- {role}")
                    
                    st.header("ATS Keywords")
                    st.write("Industry-relevant keywords that can improve your resume's performance in Applicant Tracking Systems (ATS).")
                    ats_keywords = result.get("ats_keywords", [])
                    if isinstance(ats_keywords, list):
                        for keyword in ats_keywords:
                            st.markdown(f"- {keyword}")
                    else:
                        st.json(ats_keywords)
                    
                    st.header("Project Suggestions")
                    st.write("Suggestions to improve your listed projects and new project ideas to further enhance your resume:")
                    project_suggestions = result.get("project_suggestions", {})
                    st.subheader("Improvement Tips for Existing Projects")
                    for tip in project_suggestions.get("improvement_tips", []):
                        st.markdown(f"- {tip}")
                    st.subheader("New Project Recommendations")
                    for proj in project_suggestions.get("new_project_recommendations", []):
                        st.markdown(f"- {proj}")
                    
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
            
            # Extracting and grouping skills
            top_current_skills = get_top_skills(df['Skills'])
            top_recommended_skills = get_top_skills(df['Recommended Skills'])
            
            # Creating side-by-side columns for proper alignment
            col1, col2 = st.columns(2)
            
            # Plot Pie Chart Function
            def plot_pie(ax, data, title):
                data.plot.pie(ax=ax, autopct='%1.1f%%', startangle=140, wedgeprops={'edgecolor': 'white'}, legend=False)
                ax.set_ylabel('')
                ax.set_title(title)
            
            # Creating subplots to maintain the same figure size
            fig, axes = plt.subplots(1, 2, figsize=(16, 8))
            
            # Plot both charts with the same size
            plot_pie(axes[0], top_current_skills, "Current Skills")
            plot_pie(axes[1], top_recommended_skills, "Recommended Skills")
            
            # Display the figure in Streamlit
            st.pyplot(fig)

