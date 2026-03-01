import streamlit as st
import json
import os
import sys

# Ensure paths
page_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.abspath(os.path.join(page_dir, ".."))
project_root = os.path.abspath(os.path.join(app_dir, ".."))
for p in [app_dir, project_root]:
    if p not in sys.path: sys.path.insert(0, p)

from utils.styling import apply_custom_styling
from components.paper_card import render_paper_card

st.set_page_config(page_title="Paper Library", page_icon="📚", layout="wide")
apply_custom_styling()

st.title("Paper Library")

# Init session
if 'rag' not in st.session_state:
    from utils.session import init_session_state
    init_session_state()

root = st.session_state.get('project_root', project_root)
CATALOG_PATH = os.path.join(root, "papers", "paper_catalog.json")

@st.cache_data
def load_catalog():
    if os.path.exists(CATALOG_PATH):
        try:
            with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f).get("papers", [])
        except Exception:
            return []
    return []

all_papers = load_catalog()

# Filters Sidebar
with st.sidebar:
    st.header("Library Filters")
    search_query = st.text_input("Search Title/Abstract", "")
    
    auth_list = sorted(list(set([a for p in all_papers for a in p.get('authors', [])])))
    filter_author = st.selectbox("Author", ["All"] + auth_list)
    
    year_list = sorted(list(set([str(p.get('year', '')) for p in all_papers if p.get('year')])), reverse=True)
    filter_year = st.selectbox("Year", ["All"] + year_list)

    topic_list = sorted(list(set([t for p in all_papers for t in p.get('topics', [])])))
    filter_topic = st.selectbox("Topic", ["All"] + topic_list)

    if st.button("Reset All Filters", use_container_width=True):
        st.rerun()

# Filter logic
filtered_papers = []
for p in all_papers:
    # Text search
    if search_query.lower() not in p.get('title', '').lower() and \
       search_query.lower() not in p.get('abstract', '').lower():
        continue
    
    # Author filter
    if filter_author != "All" and filter_author not in p.get('authors', []):
        continue
        
    # Year filter
    if filter_year != "All" and str(p.get('year', '')) != filter_year:
        continue
    
    # Topic filter
    if filter_topic != "All" and filter_topic not in p.get('topics', []):
        continue
        
    filtered_papers.append(p)

# Header Stats
available = [p for p in filtered_papers if os.path.exists(os.path.join(root, "papers", p.get('filename', '')))]
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Papers in View", value=len(filtered_papers))
with col2:
    st.metric(label="PDFs Available", value=len(available))
with col3:
    st.metric(label="Total in Catalog", value=len(all_papers))

st.divider()

# Ingestion Control
st.subheader("Vector Database Ingestion")
if st.button("Ingest Available PDFs"):
    if not st.session_state.get('rag_initialized'):
        st.error("System not initialized.")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        success_count = 0
        for i, paper in enumerate(available):
            pdf_path = os.path.join(root, "papers", paper.get('filename', ''))
            status_text.text(f"Ingesting: {paper.get('id')}...")
            
            try:
                chunks_added = st.session_state.rag.add_paper(pdf_path, paper)
                if chunks_added > 0:
                    success_count += 1
            except Exception as e:
                st.error(f"Error {paper['id']}: {e}")
                
            progress_bar.progress((i + 1) / len(available))
            
        status_text.text(f"Completed! {success_count} papers added to vector store.")

st.divider()

# List Papers
st.subheader("Catalog Entries")
if not filtered_papers:
    st.info("No papers match your filters.")
else:
    for paper in filtered_papers:
        render_paper_card(paper)
