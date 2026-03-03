import streamlit as st
import os
import sys

def get_project_root() -> str:
    """Returns the absolute path to the project root."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(here, '..', '..'))

def ensure_paths(project_root: str):
    """Ensures that the project root and app dir are in sys.path."""
    app_dir = os.path.join(project_root, 'app')
    for p in [project_root, app_dir]:
        if p not in sys.path:
            sys.path.insert(0, p)

def init_session_state():
    """Initializes global session variables including the RAG pipeline."""
    project_root = get_project_root()
    ensure_paths(project_root)
    
    # Load env (Local .env)
    from dotenv import load_dotenv
    load_dotenv(os.path.join(project_root, '.env'))
    
    # Bridge Streamlit Secrets to Environment Variables (for Cloud Deployment)
    try:
        if "OPENAI_API_KEY" in st.secrets:
            os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
    except Exception:
        # Ignore if no secrets found locally - will fallback to .env
        pass
    
    if 'project_root' not in st.session_state:
        st.session_state.project_root = project_root

    if 'chunk_size' not in st.session_state:
        st.session_state.chunk_size = 512
    
    if 'rag_engine' not in st.session_state:
        from src.rag_engine import RAGPipeline
        try:
            st.session_state.rag_engine = RAGPipeline(
                project_root=project_root, 
                chunk_size=st.session_state.chunk_size
            )
            st.session_state.rag_engine_ready = True
        except Exception as e:
            st.session_state.rag_engine = None
            st.session_state.rag_engine_ready = False
            st.session_state.rag_error = str(e)
            
    if "messages" not in st.session_state:
        st.session_state.messages = []
