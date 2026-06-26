import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
from dotenv import load_dotenv
from ingestion.chunker import chunk_all_docs
from ingestion.embedder import embed_chunks

load_dotenv()

def get_connection():
    return psycopg2.connect(os.getenv("SUPABASE_DATABASE_URL", ""))

def clear_existing_chunks():
    """Clear old chunks before re-ingesting so we don't get duplicates."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM document_chunks;")
    conn.commit()
    cursor.close()
    conn.close()
    print("Cleared existing chunks.")

def store_chunks(embedded_chunks: list[dict]):
    """Store embedded chunks in Supabase pgvector table."""
    conn = get_connection()
    cursor = conn.cursor()

    for chunk in embedded_chunks:
        # Convert Python list to postgres vector format
        embedding_str = "[" + ",".join(str(x) for x in chunk["embedding"]) + "]"
        cursor.execute("""
            INSERT INTO document_chunks (content, source, embedding)
            VALUES (%s, %s, %s::vector);
        """, (chunk["content"], chunk["source"], embedding_str))

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Stored {len(embedded_chunks)} chunks in Supabase.")

def run():
    print("=== UMExchange Docs Ingestion Pipeline ===\n")

    print("Step 1: Chunking docs...")
    chunks = chunk_all_docs()

    print("\nStep 2: Generating embeddings...")
    embedded = embed_chunks(chunks)

    print("\nStep 3: Clearing old data...")
    clear_existing_chunks()

    print("\nStep 4: Storing in Supabase...")
    store_chunks(embedded)

    print("\nIngestion complete.")

if __name__ == "__main__":
    run()