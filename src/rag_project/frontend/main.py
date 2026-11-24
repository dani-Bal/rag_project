from typing import TypedDict, cast
from urllib import response

import requests
import streamlit as st


class ChatMessage(TypedDict):
    role: str
    content: str


API_URL_upload = "http://backend:8000/documents/upload"
API_URL_questions = "http://backend:8000/questions"

st.set_page_config(page_title="RAG system")

st.title("Examplary RAG system Frontend")

# sidebar model selector
model = st.sidebar.selectbox("Choose Local Model", ["llama3.1", "qwen3.5", "gemma3:1b"])

# Upload functionality

# Create a button for upload
st.header("Upload of files")
uploaded_file = st.file_uploader(
    "Choose a file to be uploaded (allowed: docx, md, pdf, txt)", type=["txt", "pdf", "docx", "md"]
)

# Upload the chosen file
if uploaded_file is not None:
    st.write("Chosen file:", uploaded_file.name)
    uploadButton: bool = st.button("Upload file")
    if uploadButton:
        # If a file is uploaded, send it to the backend
        if uploaded_file is not None:
            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    uploaded_file.type,
                )
            }

            response = requests.post(API_URL_upload, files=files)
            st.write("Button clicked")
            st.write("Status Code:", response.status_code)
            st.write("Response Text:", response.text)

            if response.status_code == 201:
                data = response.json()
                st.success("Datei erfolgreich hochgeladen!")
                st.json(data)

            elif response.status_code == 400:
                st.error("Die Datei ist leer.")

            elif response.status_code == 413:
                st.error("Die Datei ist zu groß.")

            elif response.status_code == 415:
                st.error(response.json()["detail"])

            else:
                st.error(f"Fehler ({response.status_code}): {response.text}")


# Start of Chat
st.header("RAG Chatbot")

# Chat memory
if "messages" not in st.session_state:
    st.session_state.messages = []

messages: list[ChatMessage] = cast(
    list[ChatMessage],
    st.session_state["messages"],
)

# Write Chat memory
for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# user input
user_input = st.chat_input("Ask something...")

if user_input:
    messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    # Send user input to backend
    response = requests.post(API_URL_questions, json={"question": user_input})

    # Process the response
    if response.status_code == 200:
        data = response.json()
        reply = data.get("answer", "No answer received.")
        sources = data.get("sources", [])
        messages.append({"role": "assistant", "content": reply})
        messages.append({"role": "assistant", "content": f"Sources: {sources}"})
    else:
        reply = f"Fehler {response.status_code}: {response.text}"

    with st.chat_message("assistant"):
        st.markdown(reply)
        st.markdown(f"Sources: {sources}")
