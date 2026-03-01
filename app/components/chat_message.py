import streamlit as st

def render_chat_message(role: str, content: str | dict):
    """
    Renders a chat message, formatting JSON nicely if it's a dict.
    """
    with st.chat_message(role):
        if isinstance(content, dict):
            st.json(content)
        else:
            st.markdown(content)
