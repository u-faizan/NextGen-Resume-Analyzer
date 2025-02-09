import streamlit as st
# Streamlit App Title
st.title("DeepSeek Chatbot")
st.caption("Chat with the Deepseek R1 model powered by OpenRouter API")

# API Configuration
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = st.secrets["API_KEY"]  # Make sure your API key is securely stored in .streamlit/secrets.toml

# Initialize message log in session state
if "message_log" not in st.session_state:
    st.session_state.message_log = [{"role": "ai", "content": "Hello! How can I assist you today? ðŸ˜Š"}]

# Display Chat History
for message in st.session_state.message_log:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
user_input = st.chat_input("Type your message and press Enter...")

if user_input:
    # Display user input immediately
    st.session_state.message_log.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.markdown(user_input)

    # Prepare API request
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

    # Error Handling
    if response.status_code == 200:
        response_data = response.json()
        
        if "choices" in response_data:
            ai_response = response_data["choices"][0]["message"]["content"]
            st.session_state.message_log.append({"role": "ai", "content": ai_response})

            with st.chat_message("ai"):
                st.markdown(ai_response)
        else:
            error_message = response_data.get("error", {}).get("message", "Unexpected response structure.")
            st.session_state.message_log.append({"role": "ai", "content": f"Error: {error_message}"})
            
            with st.chat_message("ai"):
                st.markdown(f"Error: {error_message}")
    else:
        # Handle HTTP errors
        error_message = response.json().get('error', {}).get('message', f"HTTP {response.status_code} Error")
        st.session_state.message_log.append({"role": "ai", "content": f"Error: {error_message}"})
        
        with st.chat_message("ai"):
            st.markdown(f"Error: {error_message}")
