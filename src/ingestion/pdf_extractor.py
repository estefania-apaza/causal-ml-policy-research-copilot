import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path: str) -> dict:
    """
    Extract text and metadata from a PDF file.
    Returns: dict with keys: text, metadata, pages, extraction_warnings
    """
    doc = fitz.open(pdf_path)
    full_text = ""
    pages = []
    warnings = []

    for page_num, page in enumerate(doc):
        text = page.get_text()
        if not text.strip():
            warnings.append(f"Page {page_num + 1} looks empty or might contain an image.")
            
        pages.append({
            "page_number": page_num + 1,
            "text": text,
            "char_count": len(text)
        })
        full_text += f"\n[PAGE {page_num + 1}]\n{text}"

    # Document metadata
    metadata = doc.metadata

    return {
        "text": full_text,
        "metadata": metadata,
        "pages": pages,
        "total_pages": len(doc),
        "extraction_warnings": warnings
    }
