import streamlit as st
import requests
import json

# Streamlit App Title
st.title("DeepSeek Chatbot")
st.caption("Chat with the Deepseek R1 model powered by OpenRouter API")

# API Configuration
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = st.secrets["api"]["api_key"]  # Securely accessing API key from secrets

# Display API Key (for debugging, show only first 5 characters)
st.write(f"API Key Loaded: {API_KEY[:5]}***")

# Prepare API request without 'Bearer'
headers = {
    "Authorization": API_KEY,  # No 'Bearer' prefix
    "Content-Type": "application/json"
}

# Simple payload for testing
payload = {
    "model": "deepseek/deepseek-r1-distill-llama-70b:free",
    "messages": [{"role": "user", "content": "Hello, how are you?"}]
}

# Make API Request
response = requests.post(API_URL, headers=headers, data=json.dumps(payload))

# Handle API Response
if response.status_code == 200:
    st.success("API connection successful!")
    st.write(response.json()["choices"][0]["message"]["content"])
else:
    st.error(f"API Error {response.status_code}: {response.json().get('error', {}).get('message', 'Unknown error')}")
