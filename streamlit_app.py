import streamlit as st
import subprocess
import os
from pdfminer.high_level import extract_text
from langchain_ollama.llms import OllamaLLM

# Function to install Ollama and pull the Deepseek R1 model
def install_and_setup_ollama():
    st.info("Setting up Ollama and pulling the Deepseek R1 model. This may take a few minutes...")
    subprocess.run(['sudo', 'apt', 'update'], check=True)
    subprocess.run(['sudo', 'apt', 'install', '-y', 'pciutils'], check=True)
    subprocess.run(['curl', '-fsSL', 'https://ollama.com/install.sh', '|', 'sh'], shell=True, check=True)
    subprocess.run(['ollama', 'pull', 'deepseek:latest'], check=True)

# Run the setup (only if needed)
if not os.path.exists('/usr/local/bin/ollama'):
    install_and_setup_ollama()

# Streamlit App
st.title("NextGen Resume Analyzer")

# Upload Resume Widget
uploaded_file = st.file_uploader("Upload your resume (PDF format)", type="pdf")

if uploaded_file:
    with open("uploaded_resume.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.success("Resume uploaded successfully!")
    
    # Extract text from the uploaded resume
    resume_text = extract_text("uploaded_resume.pdf")

    # Prepare prompt for the model
    prompt = (
        """
        You are an expert resume analyzer. Extract and output the following information strictly in JSON format. 
        Do not include any explanations, comments, or additional text outside the JSON block.

        Allowed JSON keys are ONLY the following. Do not create new keys or modify these key names:
        "basic_info", "skills", "course_recommendations", "appreciation", 
        "resume_tips", "resume_score", "ai_resume_summary", "matching_job_roles", 
        "ats_keywords", "project_suggestions"

        Here is the resume text:
        """
        + resume_text +
        """
        """
    )

    # Call the model
    llm = OllamaLLM(model="deepseek:latest")
    response = llm.invoke(prompt)

    # Display the model response
    st.subheader("Resume Analysis Report")
    st.json(response)
else:
    st.info("Please upload your resume to proceed with the analysis.")
