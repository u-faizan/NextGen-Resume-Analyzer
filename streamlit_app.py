import streamlit as st
import requests
import json
import time

# Streamlit App Title
st.title("DeepSeek Chatbot")
st.caption("Chat with the Deepseek R1 model powered by OpenRouter API")

# API Configuration
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = "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"  # Replace with your valid API key

# Cooldown time between requests (in seconds)
COOLDOWN_PERIOD = 5

# Initialize message log in session state
if "message_log" not in st.session_state:
    st.session_state.message_log = [{"role": "ai", "content": "Hello! How can I assist you today? 😊"}]

# Initialize cooldown tracker
if "last_request_time" not in st.session_state:
    st.session_state.last_request_time = 0

# Display Chat History
for message in st.session_state.message_log:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
user_input = st.chat_input("Type your message and press Enter...")

if user_input:
    current_time = time.time()

    # Check if enough time has passed since the last API request
    if current_time - st.session_state.last_request_time < COOLDOWN_PERIOD:
        st.warning(f"Please wait {COOLDOWN_PERIOD} seconds between messages to avoid excessive requests.")
    else:
        # Display user input immediately
        st.session_state.message_log.append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.markdown(user_input)

        # Prepare API request
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type":
