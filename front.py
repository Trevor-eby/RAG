import streamlit as st
import sys
import os
import subprocess
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from query_data import query_rag
from file_processing import process_and_add_file_to_db

truenas_ip = "10.0.0.12"
share_name = "Files"
username = os.environ.get("TRUENAS_USERNAME")
password = os.environ.get("TRUENAS_PASSWORD")
local_mount_point = r"\\TRUENAS\\Files"

# Optional: Attempt mounting if path doesn't exist
if not os.path.exists(local_mount_point):
    os.system(f'net use {local_mount_point} \\\\{truenas_ip}\\{share_name} {password} /user:{username}')

st.title(":blue[Study App]")

# Initialize session state for chat history if missing
if "chat_history" not in st.session_state:
    # Each element: {"question": ..., "answer": ...}
    st.session_state.chat_history = []

prompt = st.chat_input("Ask a Question", accept_file=True)


if prompt:
    # Display text input if present
    if prompt.text.strip():
        user_question = prompt.text
        response = query_rag(user_question)

        # Append Q&A to session state
        st.session_state.chat_history.append({
            "question": user_question,
            "answer": response
        })


    # Handle file uploads
    if prompt.files:
        for uploaded_file in prompt.files:
            destination_path = os.path.join(local_mount_point, uploaded_file.name)
            file_content = uploaded_file.read()

            if not file_content:
                st.error(f"{uploaded_file.name} is empty or unreadable.")
                continue

            try:
                with open(destination_path, "wb") as f:
                    f.write(file_content)
                st.success(f"Uploaded {uploaded_file.name} to {destination_path}")

                # Update vector DB with new file
                process_and_add_file_to_db(destination_path)
                st.success(f"Updated database with {uploaded_file.name}")
                
            except Exception as e:
                st.error(f"Failed to upload {uploaded_file.name}: {e}")

# Render chat history in a scrollable box with fixed height
st.markdown("""
<style>

.chat-question {
    background-color: #e0f0ff;
    color: #003366;
    padding: 8px;
    border-radius: 6px;
    font-family: monospace;
    white-space: pre-wrap;
    margin-bottom: 8px;
}
.chat-answer {
    background-color: #f0f0f0;
    color: #333333;
    padding: 8px;
    border-radius: 6px;
    font-family: monospace;
    white-space: pre-wrap;
    margin-bottom: 16px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for chat in st.session_state.chat_history:
    st.markdown(f'<div class="chat-question"><b>Question:</b><br>{chat["question"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="chat-answer"><b>Answer:</b><br>{chat["answer"]}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)