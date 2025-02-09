import streamlit as st
import requests
from pdfminer.high_level import extract_text

# Streamlit App Title
st.title("📄 Resume Analyzer API Checker")
st.caption("Upload a resume and test the DeepSeek Resume Analyzer API")

# API Configuration
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = st.secrets["API_KEY"]  # Ensure your API key is securely stored in .streamlit/secrets.toml

# Function to test API connection
def test_api_connection(resume_text):
    prompt = f"Here's a sample resume text:\n\n{resume_text[:500]}\n\nCan you briefly summarize this resume?"

    headers = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek/deepseek-r1-distill-llama-70b:free",
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"API Error {response.status_code}: {response.json().get('error', {}).get('message', 'Unknown error')}"

# File uploader for PDF
uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"])

if uploaded_file:
    with open("temp_resume.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Extract text from the uploaded PDF
    resume_text = extract_text("temp_resume.pdf")
    
    st.subheader("Extracted Resume Text")
    st.text(resume_text[:500] + "...")

    if st.button("Test API Connection"):
        with st.spinner("Sending request to API..."):
            result = test_api_connection(resume_text)
        st.write(result)
