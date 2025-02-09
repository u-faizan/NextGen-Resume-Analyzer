import streamlit as st
import requests
from pdfminer.high_level import extract_text

# Streamlit App Title
st.title("DeepSeek API Test for Resume")
st.caption("Check API connectivity with a resume file")

# Secure API Key from secrets.toml
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = st.secrets["api_key"]  # Securely accessing the API key

# Upload PDF
uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"])

# Extract text from PDF
def extract_resume_text(uploaded_file):
    with open("temp_resume.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    return extract_text("temp_resume.pdf")

# API Call Function
def call_api(resume_text):
    prompt = f"Here's a sample resume text:\n\n{resume_text[:500]}\n\nCan you briefly summarize this resume?"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek/deepseek-r1-distill-llama-70b:free",
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"API Error: {e}"

# Display and Test API
if uploaded_file:
    st.success("Resume uploaded successfully!")
    resume_text = extract_resume_text(uploaded_file)

    if st.button("Test API Connection"):
        with st.spinner("Sending request to API..."):
            result = call_api(resume_text)

        st.subheader("API Response:")
        st.write(result)
