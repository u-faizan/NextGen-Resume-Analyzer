import streamlit as st
import requests
from pdfminer.high_level import extract_text

# ------------------------
# API Configuration
# ------------------------
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = "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"  # Replace with your actual API key

# Function to call API for basic response
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

# ------------------------
# Streamlit App
# ------------------------
st.set_page_config(page_title="API Test for Resume", page_icon="📄")

st.title("📄 API Test for Resume Analyzer")
uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"])

if uploaded_file:
    st.success("File uploaded successfully!")

    # Extract text from uploaded PDF
    with open("temp_resume.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    resume_text = extract_text("temp_resume.pdf")

    st.subheader("Extracted Resume Text")
    st.text(resume_text[:500] + "...")

    if st.button("Test API Connection"):
        with st.spinner("Sending request to API..."):
            result = test_api_connection(resume_text)

        st.subheader("API Response")
        st.write(result)
