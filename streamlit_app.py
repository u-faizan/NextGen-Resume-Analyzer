import streamlit as st
from PIL import Image
import json

# Page Configuration
st.set_page_config(page_title="AI-Powered Resume Analyzer", page_icon="📄", layout="wide")

# Custom CSS for advanced styling
st.markdown("""
    <style>
        body {
            background-color: #f0f2f6;
        }
        .stApp {
            background: linear-gradient(to right, #e0eafc, #cfdef3);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        h1, h2, h3 {
            color: #333;
            font-family: 'Arial', sans-serif;
        }
        .info-box {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .score-bar {
            height: 20px;
            border-radius: 10px;
            background: linear-gradient(to right, #ff6b6b, #feca57);
        }
        .recommendation {
            background-color: #f7f9fc;
            border: 1px solid #e3e6ea;
            padding: 15px;
            border-radius: 10px;
        }
        .highlight {
            color: #1e90ff;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("📄 AI-Powered Resume Analyzer")

# Basic Info Section
st.header("Resume Analysis")
with st.container():
    st.success("Hello Deepak Padhi")
    st.subheader("Your Basic Info")
    st.write("Name: **Deepak Padhi**")
    st.write("Email: **dee**")
    st.write("Contact: **84**")
    st.write("Resume Pages: **2**")
    st.markdown("<p class='highlight'>You are at intermediate level!</p>", unsafe_allow_html=True)

# Skills Section
st.header("Skills Recommendation 💡")
with st.container():
    st.subheader("Your Current Skills")
    current_skills = ["Python", "CSS", "SQL", "Engineering", "Database", "HTML", "Analyze", "C", "Website", "System", "Controls", "Github", "Analysis", "Policies", "JavaScript"]
    st.write(", ".join(current_skills))
    st.success("**Our analysis says you are looking for Web Development Jobs**")
    
    st.subheader("Recommended Skills for You")
    recommended_skills = ["React", "Django", "Node JS", "React JS", "PHP", "Laravel", "Magento", "WordPress", "JavaScript", "Angular JS", "C#", "Flask", "SDK"]
    st.write(", ".join(recommended_skills))

# Course Recommendations Section
st.header("Courses & Certificates Recommendations 🎓")
num_courses = st.slider("Choose Number of Course Recommendations:", 1, 10, 5)

# Simulated model response
model_response = '{"courses": [{"name": "Python and Django Full Stack Web Developer Bootcamp", "url": "https://www.udemy.com/course/python-and-django-full-stack-web-developer-bootcamp/"}, {"name": "Become a React Developer by Udacity", "url": "https://www.udacity.com/course/react-nanodegree--nd019"}, {"name": "Django Crash course [Free]", "url": "https://www.example.com/django-crash-course"}, {"name": "ReactJS Project Development Training", "url": "https://www.example.com/reactjs-training"}, {"name": "Full Stack Web Developer by Udacity", "url": "https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004"}]}'

# Convert JSON to Python dictionary
courses_data = json.loads(model_response)

# Display courses dynamically
for i in range(min(num_courses, len(courses_data['courses']))):
    course = courses_data['courses'][i]
    st.markdown(f"[{course['name']}]({course['url']})")

# Resume Tips & Ideas
st.header("Resume Tips & Ideas 💡")
tips = [
    ("Objective/Summary", True),
    ("Education Details", True),
    ("Experience", True),
    ("Internships", True),
    ("Skills", True),
    ("Hobbies", False),
    ("Interest", False),
    ("Achievements", False),
    ("Certifications", False),
    ("Projects", True)
]
for tip, status in tips:
    if status:
        st.markdown(f"[+] **Awesome! You have added {tip}**")
    else:
        st.markdown(f"[-] **Please add {tip}.**")

# Resume Score
st.header("Resume Score 📝")
resume_score = 66
st.markdown(f"**Your Resume Writing Score: {resume_score}**")

# Score Progress Bar
st.progress(resume_score / 100)

# Final Note
st.info("**Note: This score is calculated based on the content that you have in your Resume.**")
