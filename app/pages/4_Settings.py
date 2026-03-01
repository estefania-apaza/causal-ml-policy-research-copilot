import streamlit as st
import os
import sys

# Ensure paths
page_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.abspath(os.path.join(page_dir, ".."))
project_root = os.path.abspath(os.path.join(app_dir, ".."))
for p in [app_dir, project_root]:
    if p not in sys.path: sys.path.insert(0, p)

from utils.styling import apply_custom_styling

st.set_page_config(page_title="Settings", page_icon="📚", layout="wide")
apply_custom_styling()

st.title("Settings")

# Init session
if 'rag' not in st.session_state:
    from utils.session import init_session_state
    init_session_state()

st.subheader("RAG Engine Configuration")
st.markdown("""
Adjust the engine parameters below. 
**Note**: Changing these settings will require re-initializing the pipeline.
""")

# Chunking Configuration
current_chunk = st.session_state.get('chunk_size', 512)
new_chunk = st.radio(
    "Chunk Size Configuration",
    options=[256, 512, 1024],
    index=[256, 512, 1024].index(current_chunk),
    help="Small (256) is better for factual precision. Large (1024) is better for complex context."
)

if new_chunk != current_chunk:
    st.session_state.chunk_size = new_chunk
    # Force re-init of RAG with new chunker
    from src.rag_pipeline import RAGPipeline
    st.session_state.rag = RAGPipeline(
        project_root=st.session_state.project_root,
        chunk_size=new_chunk
    )
    st.success(f"Chunk size updated to {new_chunk} tokens.")

st.divider()

st.subheader("System Actions")
if st.button("Clear Conversation History"):
    st.session_state.messages = []
    st.success("Chat history cleared.")

if st.button("Reset Vector Database (DANGER)"):
    import shutil
    db_path = os.path.join(st.session_state.project_root, "chroma_db")
    if os.path.exists(db_path):
        shutil.rmtree(db_path)
        st.warning("Vector database deleted. You must re-ingest papers.")
        st.session_state.rag_initialized = False # Force reload
        st.rerun()
