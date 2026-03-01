import streamlit as st
import os

def render_paper_card(paper: dict):
    """
    Renders an expandable card for an academic paper catalog entry.
    """
    with st.expander(f"📄 {paper.get('id', 'N/A')}: {paper.get('title', 'Unknown Title')}", expanded=False):
        st.markdown(f"**👨‍🔬 Authors:** {', '.join(paper.get('authors', []))}")
        st.markdown(f"**📅 Year:** {paper.get('year', 'N/A')}")
        st.markdown(f"**🏛 Venue:** {paper.get('venue', 'N/A')}")
        st.markdown(f"**🔗 DOI:** {paper.get('doi', 'N/A')}")
        st.markdown(f"**🏷 Topics:** {', '.join(paper.get('topics', []))}")
        st.markdown("**📝 Abstract:**")
        st.info(paper.get('abstract', 'No abstract available.'))
        
        pdf_path = os.path.join("papers", paper.get('filename', 'missing.pdf'))
        if os.path.exists(pdf_path):
            st.success(f"✅ Local PDF found: {paper.get('filename')}")
        else:
            st.error(f"❌ PDF missing: {paper.get('filename')}. Please add it to the 'papers/' folder.")
