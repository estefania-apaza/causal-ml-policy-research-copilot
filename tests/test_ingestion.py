import traceback
import sys

def test_text_cleaner():
    try:
        from src.ingestion.text_cleaner import clean_extracted_text
        sample = "This is a    test\n12\nof the clean-\ner function."
        cleaned = clean_extracted_text(sample)
        assert "cleaner function" in cleaned
        assert "    " not in cleaned
        assert "\n12\n" not in cleaned
        print("test_text_cleaner passed!")
    except Exception as e:
        print(f"test_text_cleaner failed: {e}")
        traceback.print_exc()

def test_chunker():
    try:
        from src.chunking.chunker import TokenChunker
        chunker = TokenChunker(chunk_size=10, chunk_overlap=2)
        text = "This is a simple test text that is somewhat long so that it can be split into multiple chunks"
        chunks = chunker.chunk_text(text)
        assert len(chunks) > 1, f"Expected multiple chunks, got {len(chunks)}"
        print("test_chunker passed!")
    except Exception as e:
         print(f"test_chunker failed: {e}")
         traceback.print_exc()

if __name__ == "__main__":
    print("Running tests...")
    # These will fail if requirements aren't installed, so we wrap them in try-except
    test_text_cleaner()
    test_chunker()
    print("Done testing.")
