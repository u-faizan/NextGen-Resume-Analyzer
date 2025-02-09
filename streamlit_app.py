import streamlit as st
import requests
import json

# Streamlit App
st.title("DeepSeek Chatbot")
st.caption("Chat with the Deepseek R1 model powered by OpenRouter API")

# API Configuration
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = "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"

# Session state for managing conversation
if "message_log" not in st.session_state:
    st.session_state.message_log = [{"role": "assistant", "content": "Hello! How can I assist you today?"}]

# Display chat messages
for message in st.session_state.message_log:
    with st.chat_message("assistant" if message["role"] == "assistant" else "user"):
        st.markdown(message["content"])

# Chat input
user_input = st.chat_input("Type your message here...")

if user_input:
    # Add user message to log
    st.session_state.message_log.append({"role": "user", "content": user_input})

    # Prepare API Request
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek/deepseek-r1-distill-llama-70b:free",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            *st.session_state.message_log
        ],
        "temperature": 0.7,
        "top_p": 0.95
    }

    # Get AI response
    with st.spinner("Generating response..."):
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))

        if response.status_code == 200:
            ai_response = response.json()["choices"][0]["message"]["content"]
        else:
            ai_response = f"Error: {response.status_code} - {response.json().get('error', {}).get('message', 'Unknown error')}"

    # Add AI response to log
    st.session_state.message_log.append({"role": "assistant", "content": ai_response})

    # Rerun to update chat display
    st.rerun()
