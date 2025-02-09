import streamlit as st
import requests
import json

# Streamlit App Title
st.title("DeepSeek Chatbot")
st.caption("Chat with the Deepseek R1 model powered by OpenRouter API")

# API Configuration
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = st.secrets["API_KEY"]  # Ensure your API key is securely stored in Streamlit secrets

# Initialize session state for message log
if "message_log" not in st.session_state:
    st.session_state.message_log = [{"role": "ai", "content": "Hello! How can I assist you today? 😊"}]

# Display the chat history
for message in st.session_state.message_log:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
user_input = st.chat_input("Type your message and press Enter...")

# Only process if there's new user input
if user_input:
    # Append user message to session state
    st.session_state.message_log.append({"role": "user", "content": user_input})

    # Prepare the API request
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek/deepseek-r1-distill-llama-70b:free",
        "messages": st.session_state.message_log  # Sending entire chat history for context
    }

    # Send the request and process the response
    with st.spinner("Generating response..."):
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        try:
            ai_response = response.json()["choices"][0]["message"]["content"]
            st.session_state.message_log.append({"role": "ai", "content": ai_response})
            # Display AI response immediately
            with st.chat_message("ai"):
                st.markdown(ai_response)
        except (KeyError, IndexError):
            error_message = "Unexpected response format from API."
            st.session_state.message_log.append({"role": "ai", "content": error_message})
            with st.chat_message("ai"):
                st.markdown(error_message)
    else:
        error_message = response.json().get('error', {}).get('message', 'Unknown error occurred.')
        st.session_state.message_log.append({"role": "ai", "content": f"Error {response.status_code}: {error_message}"})
        with st.chat_message("ai"):
            st.markdown(f"Error {response.status_code}: {error_message}")
