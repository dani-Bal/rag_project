import subprocess
import streamlit as st

st.set_page_config(page_title="AI chatbot")

st.title("Chatbot with Ollama")
st.caption("Example frontend for testing local LLMs")

# sidebar model selector
model = st.sidebar.selectbox("Choose Local Model", ["llama3.1", "qwen3.5", "gemma3:1b"])

# Chat memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat memory
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# user input
user_input = st.chat_input("Ask something...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    # Call Ollama
    result = subprocess.run(["ollama", "run", model, user_input], capture_output=True, text=True)

    reply = result.stdout.strip()

    st.session_state.messages.append({"role": "assistant", "content": reply})

    with st.chat_message("assistant"):
        st.markdown(reply)
