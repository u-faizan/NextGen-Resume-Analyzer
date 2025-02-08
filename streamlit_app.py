import streamlit as st
from openai import OpenAI

# Streamlit App
st.title("DeepSeek Chatbot")
st.caption("Chat with the Deepseek R1 model powered by OpenRouter API")

# Sidebar for API Key and model selection
with st.sidebar:
    st.header("Model Configuration")
    api_key = st.text_input("Enter your OpenRouter API Key", type="password")
    selected_model = st.selectbox(
        "Choose Model",
        ["deepseek/deepseek-r1-distill-llama-70b:free"],
        index=0
    )
    st.markdown("Built with [OpenRouter](https://openrouter.ai/) | [OpenAI](https://openai.com/)")

# Initialize the OpenAI client
if api_key:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
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
                model=selected_model,
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
else:
    st.warning("Please enter your OpenRouter API Key to start chatting.")
