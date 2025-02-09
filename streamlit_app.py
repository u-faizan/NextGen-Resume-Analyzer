import streamlit as st
import requests
import json
import time

# Streamlit App Title
st.title("DeepSeek Chatbot")
st.caption("Chat with the Deepseek R1 model powered by OpenRouter API")

# API Configuration
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = st.secrets["API_KEY"]  # Store your API key in Streamlit secrets for safety

# Initialize message log and last API call timestamp in session state
if "message_log" not in st.session_state:
    st.session_state.message_log = [{"role": "ai", "content": "Hello! How can I assist you today?"}]
if "last_api_call" not in st.session_state:
    st.session_state.last_api_call = 0

# Display Chat History
for message in st.session_state.message_log:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
user_input = st.chat_input("Type your message here...")

if user_input:
    # Add user message to the session log
    st.session_state.message_log.append({"role": "user", "content": user_input})

    # Rate limiting: Ensure at least 5 seconds between API calls
    current_time = time.time()
    if current_time - st.session_state.last_api_call < 5:
        st.warning("Please wait a few seconds before sending another message.")
    else:
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
            error_message = response.json().get('error', {}).get('message', 'Unknown error')
            ai_response = f"Error {response.status_code}: {error_message}"
            st.session_state.message_log.append({"role": "ai", "content": ai_response})

        # Update last API call timestamp
        st.session_state.last_api_call = current_time
