import streamlit as st # type: ignore
import os
import sys
import pandas as pd # type: ignore
import json
import plotly.express as px # type: ignore

# Ensure paths
page_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.abspath(os.path.join(page_dir, ".."))
project_root = os.path.abspath(os.path.join(app_dir, ".."))
for p in [app_dir, project_root]:
    if p not in sys.path: sys.path.insert(0, p)

from utils.styling import apply_custom_styling # type: ignore

st.set_page_config(page_title="Analytics", page_icon="📚", layout="wide")
apply_custom_styling()

st.title("Analytics")

# Init
if 'rag' not in st.session_state:
    from utils.session import init_session_state # type: ignore
    init_session_state()

rag = st.session_state.get('rag')
root = st.session_state.get('project_root', project_root)

if not st.session_state.get('rag_initialized'):
    st.warning("Please initialize system on the Main page.")
    st.stop()

# Theme Color for charts
THEME_COLOR = "#d1495b"

try:
    collection = rag.vector_store.collection
    count = collection.count()

    # Top Level Metrics
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Total Chunks", count)
    
    data = None
    if count > 0:
        data = collection.get(include=['metadatas'])
        df_meta = pd.DataFrame([m for m in data['metadatas'] if m])
        unique_papers = df_meta['paper_id'].unique()
        
        with m2:
            st.metric("Unique Papers Indexed", len(unique_papers))
        with m3:
            st.metric("Avg Chunks per Paper", round(count / len(unique_papers), 1) if len(unique_papers) > 0 else 0)

    st.divider()

    if count > 0 and not df_meta.empty:
        # Professional Plotly Charts
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            st.subheader("Chunks per Paper")
            paper_counts = df_meta['paper_id'].value_counts().reset_index()
            paper_counts.columns = ['Paper ID', 'Count']
            fig1 = px.bar(paper_counts, x='Paper ID', y='Count', 
                         color_discrete_sequence=[THEME_COLOR],
                         template="plotly_white")
            fig1.update_layout(margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig1, use_container_width=True)

        with col_c2:
            st.subheader("Content by Year")
            year_counts = df_meta.drop_duplicates('paper_id')['year'].value_counts().reset_index()
            year_counts.columns = ['Year', 'Paper Count']
            fig2 = px.bar(year_counts, x='Year', y='Paper Count',
                         color_discrete_sequence=["#f8bbd0"], # Lighter pink
                         template="plotly_white")
            fig2.update_layout(margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig2, use_container_width=True)

        st.divider()
        
        # 3. Database Overview (The Table)
        st.subheader("Vector Database Explorer")
        st.markdown("Preview the raw data stored in your local ChromaDB vector store.")
        
        # Add a filter for the table so it's not just the first paper
        selected_preview_paper = st.selectbox("Show Preview for Paper:", ["All"] + list(unique_papers))
        
        if selected_preview_paper != "All":
            table_df = df_meta[df_meta['paper_id'] == selected_preview_paper]
            rows_to_show = table_df.head(20).copy()
        else:
            table_df = df_meta
            # Show a sample of 20 to see diverse papers
            rows_to_show = table_df.sample(min(20, len(table_df))).copy()
            
        rows_to_show = rows_to_show[['paper_id', 'chunk_id', 'title', 'year']]
        rows_to_show.columns = ['Paper', 'Chunk', 'Title', 'Year']
        
        st.dataframe(rows_to_show, use_container_width=True)
        st.caption(f"Showing a sample of up to 20 chunks. Total chunks in view: {len(table_df)}")

    else:
        st.info("Database is empty. Visit the Papers page to ingest data.")

except Exception as e:
    st.error(f"Error loading analytics: {e}")
