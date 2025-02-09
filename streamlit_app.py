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
            model="deepseek/deepseek-r1-distill-llama-70b:free",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                *st.session_state.message_log
            ]
        )
        response = completion.choices[0].message.content

    # Add AI response to log
    st.session_state.message_log.append({"role": "ai", "content": response})

    # Rerun to update chat display
    st.rerun()
