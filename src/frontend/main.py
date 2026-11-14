import streamlit as st
import subprocess
import os

st.set_page_config(page_title="AI chatbot")

st.title("Examplary RAG system Frontend")
st.caption("to be adapted as needed")

# sidebar model selector
model = st.sidebar.selectbox(
    "Choose Local Model",
    ["llama3.1", "qwen3.5", "gemma3:1b"]
)

# Upload functionality
# Define Upload-Ordner
upload_folder = "UploadedFiles"

# Create a button for upload
st.header("Upload of files")
uploaded_file = st.file_uploader("Choose a file to be uploaded (allowed: docx, md, pdf, txt)", type=["txt", "pdf", "docx", "md"])

# Actually upload the chosen file
if uploaded_file is not None:
    st.write("Chosen file:", uploaded_file.name)
    if st.button("Upload file"):
        # Überprüfe, ob die Datei erfolgreich hochgeladen wurde
        if uploaded_file is not None:
            filename = uploaded_file.name
            filepath = os.path.join(upload_folder, filename)
            with open(filepath, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("The file was uploaded successfully!")
        else:
            st.error("Error while uploading the file")

            

# Start of Chat
st.header("AI Chatbot with local LLMs via Ollama")

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
    st.session_state.messages.append({"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)
    
    
    #Call Ollama
    result = subprocess.run(
        ["ollama", "run", model, user_input],
        capture_output=True,
        text=True
    )

    reply = result.stdout.strip()

    st.session_state.messages.append({"role": "assistant", "content": reply}
    )

    with st.chat_message("assistant"):
        st.markdown(reply) 
