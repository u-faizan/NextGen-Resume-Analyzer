import streamlit as st
import requests
from pdfminer.high_level import extract_text

# Read API Key from secrets
API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

def test_api_connection(resume_text):
    prompt = f"Here's a sample resume text:\n\n{resume_text[:500]}\n\nCan you briefly summarize this resume?"

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
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"API Error {response.status_code}: {response.json().get('error', {}).get('message', 'Unknown error')}"

# Streamlit Interface
st.title("📄 API Test for Resume Analyzer")
uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"])

if uploaded_file:
    with open("temp_resume.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    resume_text = extract_text("temp_resume.pdf")
    
    if st.button("Test API Connection"):
        with st.spinner("Sending request to API..."):
            result = test_api_connection(resume_text)
        st.write(result)
