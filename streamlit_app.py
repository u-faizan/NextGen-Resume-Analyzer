import streamlit as st
import requests
import json

# Streamlit App Title
st.title("DeepSeek Chatbot")
st.caption("Chat with the Deepseek R1 model powered by OpenRouter API")

# API Configuration
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = st.secrets["api"]["api_key"]  # Ensure API key is securely stored in .streamlit/secrets.toml

# Verify API Key is Loaded (for debugging)
st.write(f"API Key Loaded: {API_KEY[:5]}***")

# Prepare API request with Bearer prefix
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Simple payload to test the API
payload = {
    "model": "deepseek/deepseek-r1-distill-llama-70b:free",
    "messages": [{"role": "user", "content": "Hello, how are you?"}]
}

# Send request to the API
response = requests.post(API_URL, headers=headers, data=json.dumps(payload))

# Handle API Response
if response.status_code == 200:
    st.success("API connection successful!")
    st.write(response.json()["choices"][0]["message"]["content"])
else:
    st.error(f"API Error {response.status_code}: {response.json().get('error', {}).get('message', 'Unknown error')}")
