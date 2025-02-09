import streamlit as st
import requests
import json

# Streamlit App Title
st.title("DeepSeek Chatbot")
st.caption("Chat with the Deepseek R1 model powered by OpenRouter API")

# API Configuration
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = "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"  # Replace with your actual API key

# Initialize message log in session state
if "message_log" not in st.session_state:
    st.session_state.message_log = [{"role": "ai", "content": "Hello! How can I assist you today?"}]

# Display Chat History
for message in st.session_state.message_log:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
user_input = st.chat_input("Type your message here...")

if user_input and "last_input" not in st.session_state:
    st.session_state.last_input = user_input  # Store the last input to avoid repeated API calls

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
        error_message = response.json().get('error', {}).get('message', 'Unknown error')
        ai_response = f"Error {response.status_code}: {error_message}"
        st.session_state.message_log.append({"role": "ai", "content": ai_response})

    del st.session_state.last_input  # Remove last_input after processing
