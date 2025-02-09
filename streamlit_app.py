import streamlit as st
import requests
from pdfminer.high_level import extract_text

# API Configuration
API_KEY = "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"  # Replace with your API Key
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Function to Test API Connection
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

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"API Error: {e}"

# Streamlit Interface
st.title("📄 API Test for Resume Analyzer")
uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"])

# Ensure API call only triggers on button click
if "api_called" not in st.session_state:
    st.session_state.api_called = False

if uploaded_file and st.button("Test API Connection"):
    with open("temp_resume.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    resume_text = extract_text("temp_resume.pdf")

    with st.spinner("Sending request to API..."):
        result = test_api_connection(resume_text)
    
    st.session_state.api_called = True
    st.session_state.api_result = result

# Display result only after API call
if st.session_state.api_called:
    st.subheader("API Response:")
    st.write(st.session_state.api_result)
