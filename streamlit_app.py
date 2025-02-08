import streamlit as st
import subprocess
import os
from pdfminer.high_level import extract_text
from langchain_ollama.llms import OllamaLLM

st.title('NextGen Resume Analyzer')

# Function to install Ollama and pull the deepseek model
def install_ollama_and_model():
    try:
        subprocess.run(['sudo', 'apt', 'update'], check=True)
        subprocess.run(['sudo', 'apt', 'install', '-y', 'pciutils'], check=True)
        subprocess.run(['curl', '-fsSL', 'https://ollama.com/install.sh', '|', 'sh'], shell=True, check=True)
        subprocess.run(['ollama', 'pull', 'deepseek:latest'], check=True)
        st.success("Ollama installed and deepseek model pulled successfully!")
    except subprocess.CalledProcessError as e:
        st.error(f"Error during installation: {e}")

# Streamlit UI
st.title("NextGen Resume Analyzer")

# Button to install Ollama and download the model
if st.button("Install Ollama & Download Model"):
    install_ollama_and_model()

# Widget to upload resume
uploaded_file = st.file_uploader("Upload your Resume (PDF format)", type=["pdf"])

if uploaded_file is not None:
    # Extract text from uploaded PDF
    with open("temp_resume.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    resume_text = extract_text("temp_resume.pdf")
    
    st.subheader("Extracted Resume Text")
    st.text(resume_text)

    # Analyze the resume using Ollama
    if st.button("Analyze Resume"):
        prompt = f"""
        You are an expert resume analyzer. Extract and output the following information strictly in JSON format. Do not include any explanations or additional text outside the JSON block.

        Allowed JSON keys: "basic_info", "skills", "course_recommendations", "appreciation", "resume_tips", "resume_score", "ai_resume_summary", "matching_job_roles", "ats_keywords", "project_suggestions"

        Here is the resume text:
        """
        {resume_text}
        """
        
        llm = OllamaLLM(model="deepseek")
        response = llm.invoke(prompt)

        st.subheader("Model Response")
        st.json(response)

# Clean up temporary file
if os.path.exists("temp_resume.pdf"):
    os.remove("temp_resume.pdf")

