import os

DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs")

CHUNK_SIZE = 500
OVERLAP = 100

def load_docs() -> list[dict]:
    """Load all markdown files from the docs folder."""
    docs = []
    for filename in os.listdir(DOCS_DIR):
        if filename.endswith(".md"):
            filepath = os.path.join(DOCS_DIR, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            docs.append({
                "source": filename,
                "content": content
            })
            print(f"Loaded: {filename} ({len(content)} chars)")
    return docs

def chunk_text(text: str, source: str) -> list[dict]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0

    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end]

        # Don't store empty or whitespace-only chunks
        if chunk.strip():
            chunks.append({
                "content": chunk.strip(),
                "source": source
            })

        # Move forward by chunk size minus overlap
        start += CHUNK_SIZE - OVERLAP

    return chunks

def chunk_all_docs() -> list[dict]:
    """Load and chunk all docs, return list of chunks."""
    docs = load_docs()
    all_chunks = []

    for doc in docs:
        chunks = chunk_text(doc["content"], doc["source"])
        all_chunks.extend(chunks)
        print(f"  → {len(chunks)} chunks from {doc['source']}")

    print(f"\nTotal chunks: {len(all_chunks)}")
    return all_chunks

if __name__ == "__main__":
    chunks = chunk_all_docs()
    # Preview first 3 chunks
    for i, chunk in enumerate(chunks[:3]):
        print(f"\n--- Chunk {i+1} (source: {chunk['source']}) ---")
        print(chunk["content"])
        print(f"Length: {len(chunk['content'])} chars")