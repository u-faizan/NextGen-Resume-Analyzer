import streamlit as st
import requests
import json
import time

# Streamlit App Title
st.title("DeepSeek Chatbot")
st.caption("Chat with the Deepseek R1 model powered by OpenRouter API")

# API Configuration
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = st.secrets.get("api_key", None)  # Securely accessing API key from secrets

# Check if API Key is loaded
if not API_KEY:
    st.error("API key not found! Please check your secrets configuration.")
    st.stop()
else:
    st.success("API Key loaded successfully!")

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
            "Authorization": API_KEY,  # Directly using API key without 'Bearer'
            "Content-Type": "application/json"
        }

        payload = {
            "model": "deepseek/deepseek-r1-distill-llama-70b:free",
            "messages": st.session_state.message_log
        }

        # Get AI response
        with st.spinner("Generating response..."):
            try:
                response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
                response.raise_for_status()
                response_data = response.json()
                
                if "choices" in response_data:
                    ai_response = response_data["choices"][0]["message"]["content"]
                    st.session_state.message_log.append({"role": "ai", "content": ai_response})

                    with st.chat_message("ai"):
                        st.markdown(ai_response)
                else:
                    st.error("Unexpected response structure from API.")
            except requests.exceptions.RequestException as e:
                st.error(f"API Error: {e}")

        # Update the last request time to enforce cooldown
        st.session_state.last_request_time = time.time()
