import requests
import streamlit as st

BACKEND_URL = "http://backend:8000/chat"

st.set_page_config(
    page_title="Banking Agents Chat",
    page_icon="🏦",
)

st.title("Banking Agents Chat")

if 'conversation_id' not in st.session_state:
    st.session_state.conversation_id = None

if 'messages' not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_message = st.chat_input("Ask about banking products and consortium options...")

if user_message:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    with st.chat_message("user"):
        st.write(user_message)

    payload = {
        "message": user_message,
        "conversation_id": st.session_state.conversation_id
    }

    with st.chat_message("assistant"):
        with st.spinner("thinking"):
            response = requests.post(BACKEND_URL, json=payload, timeout=180)
            response.raise_for_status()
            data = response.json()

            st.session_state.conversation_id = data["conversation_id"]

            assistant_response = data["response"]
            selected_agent = data["agent"]

            st.caption(f"Agent: {selected_agent}")
            st.write(assistant_response)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": assistant_response,
        }
    )