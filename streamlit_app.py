import streamlit as st
from openai import OpenAI

# Streamlit App
st.title("DeepSeek")
st.caption("Chat with the Deepseek R1 model powered by OpenRouter API")

# Initialize the OpenAI client with API Key
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="sk-or-your_actual_api_key_here"
)

# Session state for managing conversation
if "message_log" not in st.session_state:
    st.session_state.message_log = [{"role": "ai", "content": "Hello! How can I assist you today?"}]

# Display chat messages
for message in st.session_state.message_log:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
user_input = st.chat_input("Type your message here...")

if user_input:
    # Add user message to log
    st.session_state.message_log.append({"role": "user", "content": user_input})

    # Get AI response
    with st.spinner("Generating response..."):
        completion = client.chat.completions.create(
            model="openai/chatgpt-4o-latest",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                *st.session_state.message_log
            ],
            extra_headers={
                "HTTP-Referer": "<YOUR_SITE_URL>",  # Optional, replace or remove if unnecessary
                "X-Title": "<YOUR_SITE_NAME>"       # Optional, replace or remove if unnecessary
            }
        )
        response = completion.choices[0].message.content

    # Add AI response to log
    st.session_state.message_log.append({"role": "ai", "content": response})

    # Rerun to update chat display
    st.rerun()
