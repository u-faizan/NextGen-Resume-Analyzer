import streamlit as st
from langchain_ollama import ChatOllama

# Streamlit App
st.title("Ollama Chatbot")
st.caption("Chat with the Deepseek R1 model powered by Ollama")

# Sidebar for model selection
with st.sidebar:
    st.header("Model Configuration")
    selected_model = st.selectbox(
        "Choose Model",
        ["deepseek-r1:1.5b", "deepseek-r1:3b"],
        index=0
    )
    st.markdown("Built with [Ollama](https://ollama.ai/) | [LangChain](https://python.langchain.com/)")

# Initialize the chat engine
llm_engine = ChatOllama(
    model=selected_model,
    base_url="http://localhost:11434",
    temperature=0.3
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
        response = llm_engine.invoke(user_input)
    
    # Add AI response to log
    st.session_state.message_log.append({"role": "ai", "content": response})
    
    # Rerun to update chat display
    st.rerun()
