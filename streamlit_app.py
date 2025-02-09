import streamlit as st
from openai import OpenAI

# Streamlit App
st.title("DeepSeek Chatbot")
st.caption("Chat with the Deepseek R1 model powered by OpenRouter API")

# Initialize the OpenAI client with API Key
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"
)

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

    # Get AI response
    with st.spinner("Generating response..."):
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "<YOUR_SITE_URL>",  # Optional. Site URL for rankings on openrouter.ai.
                "X-Title": "<YOUR_SITE_NAME>",  # Optional. Site title for rankings on openrouter.ai.
            },
            model="openai/chatgpt-4o-latest",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                *st.session_state.message_log
            ]
        )
        response = completion.choices[0].message.content

    # Add AI response to log
    st.session_state.message_log.append({"role": "assistant", "content": response})

    # Rerun to update chat display
    st.rerun()
