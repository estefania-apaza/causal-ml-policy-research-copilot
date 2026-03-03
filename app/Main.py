import streamlit as st
import os
import sys

# Ensure paths
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.session import init_session_state
from utils.styling import apply_custom_styling

st.set_page_config(
    page_title="Research Copilot",
    page_icon="📚",
    layout="wide",
)
apply_custom_styling()

from dotenv import load_dotenv
load_dotenv(os.path.join(project_root, '.env'))

st.title("Research Copilot")
st.caption("Advanced Retrieval-Augmented Generation for Causal ML Research")

# Initialize RAG
with st.spinner("Initializing Pipeline..."):
    init_session_state()

if st.session_state.get('rag_engine_ready', False):
    st.success("System ready")
else:
    error = st.session_state.get('rag_error', 'Unknown error')
    st.error(f"Error: {error}")

st.divider()

st.subheader("Welcome")
st.markdown("""
This platform allows you to interact with a library of academic papers using state-of-the-art Large Language Models. 
By indexing papers into a vector database, we enable semantic search and precise question answering with citations.

### Getting Started
1. **Explore Papers**: Visit the **Papers** page to browse the catalog and ingest PDFs into the system.
2. **Contextual Chat**: Use the **Chat** interface to query specific papers or the entire database.
3. **Analyze**: Check the **Analytics** dashboard to visualize document statistics and metadata.
""")

st.divider()

st.subheader("Prompt Engineering Strategies")
st.markdown("Select an appropriate strategy in the chat sidebar depending on your research needs:")

col1, col2 = st.columns(2)
with col1:
    with st.expander("Delimiters (Clear & Direct)"):
        st.markdown("""
Uses strict structural markers to separate context from questions. Best for high-precision extraction.
- **Use case**: Definition lookup, parameter extraction.
""")

    with st.expander("Structured JSON Output"):
        st.markdown("""
Forces the model to respond in a valid JSON schema. Useful for downstream data processing.
- **Use case**: Systematic literature review tables.
""")

with col2:
    with st.expander("Few-Shot Learning"):
        st.markdown("""
Provides the model with high-quality examples of academic reasoning to guide its response style.
- **Use case**: Complex theoretical comparisons.
""")

    with st.expander("Chain-of-Thought Reasoning"):
        st.markdown("""
Instructs the model to explicitly decompose complex problems into logical steps before answering.
- **Use case**: Synthesis of methodologies across multiple papers.
""")
