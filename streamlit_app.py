import streamlit as st
import requests
import json

# Streamlit App Title
st.title("DeepSeek Chatbot")
st.caption("Chat with the Deepseek R1 model powered by OpenRouter API")

# API Configuration
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = st.secrets["API_KEY"]  # Make sure your API key is securely stored in .streamlit/secrets.toml

# Initialize message log in session state
if "message_log" not in st.session_state:
    st.session_state.message_log = [{"role": "ai", "content": "Hello! How can I assist you today? 😊"}]

# Display Chat History
for message in st.session_state.message_log:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
user_input = st.chat_input("Type your message and press Enter...")

if user_input:
    # Display user input immediately
    st.session_state.message_log.append({"role": "user", "content": user_input})
    
    # Re-render the chat with the new user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # Prepare API request
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek/deepseek-r1-distill-llama-70b:free",
        "messages": st.session_state.message_log  # Send complete message history
    }

    # Get AI response
    with st.spinner("Generating response..."):
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        ai_response = response.json()["choices"][0]["message"]["content"]
        st.session_state.message_log.append({"role": "ai", "content": ai_response})
        
        # Display AI response immediately
        with st.chat_message("ai"):
            st.markdown(ai_response)
    else:
        error_message = response.json().get('error', {}).get('message', 'Unknown error')
        st.session_state.message_log.append({"role": "ai", "content": f"Error {response.status_code}: {error_message}"})
        
        # Display error message
        with st.chat_message("ai"):
            st.markdown(f"Error {response.status_code}: {error_message}")
