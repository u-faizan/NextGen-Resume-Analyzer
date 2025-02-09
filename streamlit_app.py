import streamlit as st
import requests
import json

API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = st.secrets["api"]["api_key"]

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": "deepseek/deepseek-r1-distill-llama-70b:free",
    "messages": [{"role": "user", "content": "Hello, how are you?"}]
}

response = requests.post(API_URL, headers=headers, data=json.dumps(payload))

if response.status_code == 200:
    st.success("API connection successful!")
    st.write(response.json()["choices"][0]["message"]["content"])
else:
    st.error(f"API Error {response.status_code}: {response.json().get('error', {}).get('message', 'Unknown error')}")
