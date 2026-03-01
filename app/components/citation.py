import streamlit as st

def format_citation(paper_meta: dict) -> str:
    """Formats metadata into an APA-like citation string."""
    authors = ", ".join(paper_meta.get("authors", []))
    year = paper_meta.get("year", "n.d.")
    title = paper_meta.get("title", "Untitled")
    venue = paper_meta.get("venue", "Unknown Venue")
    doi = paper_meta.get("doi", "")
    
    citation = f"{authors} ({year}). {title}. *{venue}*."
    if doi:
        citation += f" https://doi.org/{doi}"
    return citation

def render_citations(citations: list[dict]):
    """Renders a list of citations cleanly."""
    if not citations:
        return
        
    st.markdown("### 📚 References")
    for cit in citations:
        st.markdown(f"- {format_citation(cit)}")
