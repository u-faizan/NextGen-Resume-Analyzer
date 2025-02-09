import streamlit as st
from openai import OpenAI

# Streamlit App
st.title("DeepSeek Chatbot")

# Initialize the OpenAI client with API Key
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

# Session state for managing conversation
if "message_log" not in st.session_state:
    st.session_state.message_log = [{"role": "ai", "content": "Hello! How can I assist you today?"}]

# Display chat messages
for message in st.session_state.message_log:
    st.write(f"**{message['role'].capitalize()}:** {message['content']}")

# Chat input
user_input = st.text_input("Type your message here...")

if user_input:
    # Add user message to log
    st.session_state.message_log.append({"role": "user", "content": user_input})

    # Get AI response
    try:
        completion = client.chat.completions.create(
            model="deepseek/deepseek-r1-distill-llama-70b:free",
            messages=st.session_state.message_log,
            extra_headers={
                "HTTP-Referer": "<YOUR_SITE_URL>",
                "X-Title": "<YOUR_SITE_NAME>",
            }
        )
        response = completion.choices[0].message.content
    
        # Add AI response to log
        st.session_state.message_log.append({"role": "ai", "content": response})
    
    except Exception as e:
        st.error(f"Error: {e}")

    # Rerun to update chat display
    st.experimental_rerun()
