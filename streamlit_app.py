import streamlit as st
import requests
import json

# Streamlit App Title
st.title("DeepSeek Chatbot")
st.caption("Chat with the Deepseek R1 model powered by OpenRouter API")

# API Configuration
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = "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"  # Replace with your actual key

# Initialize message log in session state
if "message_log" not in st.session_state:
    st.session_state.message_log = [{"role": "ai", "content": "Hello! How can I assist you today?"}]

# Display Chat History
for message in st.session_state.message_log:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
user_input = st.chat_input("Type your message here...")

# Only send API request if user_input exists
if user_input:
    # Add user message to the session log
    st.session_state.message_log.append({"role": "user", "content": user_input})

    # Prepare API Request
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek/deepseek-r1-distill-llama-70b:free",
        "messages": st.session_state.message_log
    }

    # Get AI response
    with st.spinner("Generating response..."):
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        ai_response = response.json()["choices"][0]["message"]["content"]
        st.session_state.message_log.append({"role": "ai", "content": ai_response})
    else:
        ai_response = f"Error {response.status_code}: {response.json().get('error', {}).get('message', 'Unknown error')}"
        st.session_state.message_log.append({"role": "ai", "content": ai_response})

    # Rerun to display the new messages
    st.experimental_rerun()
