import streamlit as st
import subprocess
from pdfminer.high_level import extract_text
from langchain_ollama.llms import Ollama
import os

# Function to install Ollama and pull deepseek model
def install_ollama_and_pull_model():
    with st.spinner('Setting up the environment...'):
        subprocess.run(['sudo', 'apt', 'update'], check=True)
        subprocess.run(['sudo', 'apt', 'install', '-y', 'pciutils'], check=True)
        subprocess.run(['curl', '-fsSL', 'https://ollama.com/install.sh'], check=True)
        subprocess.run(['ollama', 'pull', 'deepseek:latest'], check=True)
    st.success('Ollama installed and deepseek model pulled successfully!')

# Function to extract text from PDF
def extract_resume_text(uploaded_file):
    with open("temp_resume.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    return extract_text("temp_resume.pdf")

# Function to analyze resume using LLM
def analyze_resume(resume_text):
    llm = Ollama(model="deepseek")
    prompt = f"""
    You are an expert resume analyzer. Extract and output the following information **strictly in JSON format**. **Do not include any explanations, comments, or additional text** outside the JSON block.

    **Allowed JSON keys are ONLY the following. Do not create new keys or modify these key names:**
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
        "appreciation": list of at least 5 personalized positive comments starting with "You have..." or "Your..." to acknowledge the candidate's strengths,
        "resume_tips": list of at least 5 constructive feedback points for resume improvement,
        "resume_score": string (score in "XX/100" format),
        "ai_resume_summary": string (a one-paragraph summary of the user's experience, skills, and expertise for ATS optimization),
        "matching_job_roles": list of 2-3 job roles that match the candidate's skills,
        "ats_keywords": list of at least 5 industry-relevant keywords missing from the resume to improve ATS ranking,
        "project_suggestions": list of at least 3 general, specific ways to enhance project descriptions for better clarity and impact. Mention project names if available.
    }}

    **Return only valid JSON and nothing else.**

    Here is the resume text:
    """
    {resume_text}
    """
    response = llm.invoke(prompt)
    return response

# Streamlit UI
st.title("NextGen Resume Analyzer")

# Step 1: Install Ollama and pull the model
if st.button('Setup Environment'):
    install_ollama_and_pull_model()

# Step 2: Upload resume
uploaded_file = st.file_uploader("Upload your resume (PDF only):", type=["pdf"])

if uploaded_file:
    st.success('Resume uploaded successfully!')
    resume_text = extract_resume_text(uploaded_file)
    
    # Step 3: Analyze resume
    if st.button('Analyze Resume'):
        with st.spinner('Analyzing your resume...'):
            response = analyze_resume(resume_text)
        
        # Display response
        st.subheader('Resume Analysis Results')
        st.json(response)
