import streamlit as st
from openai import OpenAI

# Streamlit App
st.title("DeepSeek")
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
            extra_headers={
                "HTTP-Referer": "https://your-site-url.com",  # Optional. Site URL for rankings on openrouter.ai.
                "X-Title": "DeepSeek Chatbot"  # Optional. Site title for rankings on openrouter.ai.
            },
            extra_body={},
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
