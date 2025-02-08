import streamlit as st
import subprocess
from langchain_ollama.llms import OllamaLLM

# Function to install Ollama and pull the Deepseek R1 model
def install_and_setup_ollama():
    st.info("Setting up Ollama and pulling the Deepseek R1 model. This may take a few minutes...")
    subprocess.run(['sudo', 'apt', 'update'], check=True)
    subprocess.run(['sudo', 'apt', 'install', '-y', 'pciutils'], check=True)
    subprocess.run(['curl', '-fsSL', 'https://ollama.com/install.sh', '|', 'sh'], shell=True, check=True)
    subprocess.run(['ollama', 'pull', 'deepseek-r1'], check=True)

# Run the setup (only if needed)
install_and_setup_ollama()

# Streamlit App
st.title("Ollama Chatbot")

# Chatbot widget
st.subheader("Chat with the Ollama LLM")
user_input = st.text_input("You:")

if user_input:
    llm = OllamaLLM(model="deepseek-r1")
    response = llm.invoke(user_input)
    st.text_area("Chatbot:", value=response, height=200, max_chars=None, key=None)
else:
    st.info("Type a message to start chatting with the bot.")
