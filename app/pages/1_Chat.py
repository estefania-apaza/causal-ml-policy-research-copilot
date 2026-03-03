import streamlit as st
import os
import sys
import json
import time

# Ensure paths
page_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.abspath(os.path.join(page_dir, ".."))
project_root = os.path.abspath(os.path.join(app_dir, ".."))
for p in [app_dir, project_root]:
    if p not in sys.path:
        sys.path.insert(0, p)

from utils.styling import apply_custom_styling
from components.chat_message import render_chat_message

st.set_page_config(page_title="Chat", page_icon="📚", layout="wide")
apply_custom_styling()

# Init
from utils.session import init_session_state
init_session_state()

if 'reset_counter' not in st.session_state:
    st.session_state.reset_counter = 0

root = st.session_state.get('project_root', project_root)

# Sidebar settings
with st.sidebar:
    st.header("Chat Settings")

    PROMPT_STRATEGIES = {
        "Delimiters (Clear & Direct)": "v1_delimiters",
        "Structured JSON Output": "v2_json_output",
        "Few-Shot Examples": "v3_few_shot",
        "Chain-of-Thought Reasoning": "v4_chain_of_thought",
    }
    selected_label = st.selectbox(
        "Prompt Strategy",
        options=list(PROMPT_STRATEGIES.keys()),
        index=0,
        help="Select the prompt engineering strategy to use."
    )
    prompt_strategy = PROMPT_STRATEGIES[selected_label]

    # Filters
    st.divider()
    st.subheader("Filters")

    catalog_path = os.path.join(root, "papers", "paper_catalog.json")
    paper_options = {"All Papers": None}
    @st.cache_data
    def load_catalog_chat(file_path, mtime):
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f).get('papers', [])
        return []

    catalog_mtime = os.path.getmtime(catalog_path) if os.path.exists(catalog_path) else 0
    all_papers_meta = load_catalog_chat(catalog_path, catalog_mtime)
    
    for p in all_papers_meta:
        label = f"{p['id']}: {p['title'][:40]}"
        paper_options[label] = p['id']

    selected_paper_label = st.selectbox("Filter by Paper", options=list(paper_options.keys()), key=f"filter_paper_{st.session_state.reset_counter}")
    paper_id_filter = paper_options[selected_paper_label]

    # Author filter
    all_authors = sorted(set(
        author.strip()
        for p in all_papers_meta
        for author in p.get('authors', [])
    ))
    selected_author = st.selectbox("Filter by Author", ["All Authors"] + all_authors, key=f"filter_author_{st.session_state.reset_counter}")

    # Year filter
    all_years = sorted(set(str(p.get('year', '')) for p in all_papers_meta if p.get('year')))
    selected_year = st.selectbox("Filter by Year", ["All Years"] + all_years, key=f"filter_year_{st.session_state.reset_counter}")

    # Topic filter
    all_topics = sorted(set(
        t for p in all_papers_meta for t in p.get('topics', [])
    ))
    selected_topic = st.selectbox("Filter by Topic", ["All Topics"] + all_topics, key=f"filter_topic_{st.session_state.reset_counter}")

    st.divider()
    # Results slider
    top_k = st.slider("Results to retrieve", min_value=3, max_value=10, value=5)

    st.divider()
    
    # Utility buttons
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Clear History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with c2:
        if st.button("Reset Filters", use_container_width=True):
            st.session_state.reset_counter += 1
            st.rerun()

# Resolve paper_id from author/year/topic filters if no paper selected
if paper_id_filter is None and (selected_author != "All Authors" or selected_year != "All Years" or selected_topic != "All Topics"):
    matching_ids = []
    for p in all_papers_meta:
        author_match = selected_author == "All Authors" or selected_author in p.get('authors', [])
        year_match = selected_year == "All Years" or str(p.get('year', '')) == selected_year
        topic_match = selected_topic == "All Topics" or selected_topic in p.get('topics', [])
        if author_match and year_match and topic_match:
            matching_ids.append(p['id'])
else:
    matching_ids = [paper_id_filter] if paper_id_filter else None

# Main chat area
st.title("Chat")

if not st.session_state.get('rag_initialized'):
    st.error("System not initialized. Go to the Main page first.")
    st.stop()

# Display history
for msg in st.session_state.get("messages", []):
    render_chat_message(msg["role"], msg["content"])

# Chat input
if user_input := st.chat_input("Ask a question about your papers..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    render_chat_message("user", user_input)

    with st.spinner("Searching papers..."):
        try:
            rag = st.session_state.rag

            # Pass history to RAG pipeline (limit to last 10 messages for token safety)
            history = st.session_state.messages[:-1][-10:]

            # Apply paper_id filter (single paper or None)
            effective_paper_id = None
            if matching_ids and len(matching_ids) == 1:
                effective_paper_id = matching_ids[0]

            response = rag.answer_question(
                user_input,
                strategy=prompt_strategy,
                paper_id=effective_paper_id,
                history=history
            )
        except Exception as e:
            response = f"Error generating answer: {e}"

    st.session_state.messages.append({"role": "assistant", "content": response})
    render_chat_message("assistant", response)
