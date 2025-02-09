import requests
import json

API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = "sk-or-your_actual_api_key_here"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://share.streamlit.io",
    "X-Title": "Test Script"
}

payload = {
    "model": "deepseek/deepseek-r1-distill-llama-70b:free",
    "messages": [{"role": "user", "content": "Is the API working outside Streamlit?"}]
}

response = requests.post(API_URL, headers=headers, data=json.dumps(payload))

if response.status_code == 200:
    print("API Success:", response.json()["choices"][0]["message"]["content"])
else:
    print("API Error:", response.status_code, response.json())
