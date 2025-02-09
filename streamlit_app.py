import streamlit as st
import requests
import json

# Streamlit App Title
st.title("DeepSeek Chatbot")
st.caption("Chat with the Deepseek R1 model powered by OpenRouter API")

# API Configuration
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = st.secrets["API_KEY"]  # Secure storage for API key

# Initialize session state
if "message_log" not in st.session_state:
    st.session_state.message_log = [{"role": "ai", "content": "Hello! How can I assist you today? 😊"}]

# Display Chat History
for message in st.session_state.message_log:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
user_input = st.chat_input("Type your message and press Enter...")

if user_input:
    # Add user's new message to session log
    st.session_state.message_log.append({"role": "user", "content": user_input})

    # Prepare API Request
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek/deepseek-r1-distill-llama-70b:free",
        "messages": st.session_state.message_log  # Send entire conversation for context
    }

    # Make API Call
    with st.spinner("Generating response..."):
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))

    # Handle API Response
    if response.status_code == 200:
        try:
            ai_response = response.json()["choices"][0]["message"]["content"]
            st.session_state.message_log.append({"role": "ai", "content": ai_response})  # Add AI response to session
        except (KeyError, IndexError):
            st.session_state.message_log.append({"role": "ai", "content": "Unexpected response format from API."})
    else:
        error_message = response.json().get('error', {}).get('message', 'Unknown error occurred.')
        st.session_state.message_log.append({"role": "ai", "content": f"Error {response.status_code}: {error_message}"})

    # Refresh chat display after new message
    st.experimental_rerun()
