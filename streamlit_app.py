import streamlit as st
import requests
import json

# Access API key from Streamlit secrets (ensure it's stored properly in secrets.toml)
API_KEY = st.secrets["api_key"]

# API Configuration
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Prepare API headers using Bearer token
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Example payload
payload = {
    "model": "deepseek/deepseek-r1-distill-llama-70b:free",
    "messages": [{"role": "user", "content": "Hello, how are you?"}]
}

# Make API request
response = requests.post(API_URL, headers=headers, data=json.dumps(payload))

# Check response
if response.status_code == 200:
    result = response.json()["choices"][0]["message"]["content"]
    st.write(result)
else:
    st.error(f"API Error {response.status_code}: {response.json().get('error', {}).get('message', 'Unknown error')}")
