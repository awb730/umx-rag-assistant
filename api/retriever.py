import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
import time
from dotenv import load_dotenv
from ingestion.embedder import embed_text

load_dotenv()

def get_connection():
    return psycopg2.connect(os.getenv("SUPABASE_DATABASE_URL", ""))

def retrieve(question: str, top_k: int = 5) -> list[dict]:
    """
    Embed the question and find the most semantically similar chunks.
    Returns top_k chunks with their content, source, and similarity score.
    """
    print(f"Retrieving chunks for: '{question}'")

    try:
        # Step 1 — embed the question
        question_embedding = embed_text(question)
        embedding_str = "[" + ",".join(str(x) for x in question_embedding) + "]"

        # Step 2 — find most similar chunks using cosine similarity
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                content,
                source,
                1 - (embedding <=> %s::vector) AS similarity
            FROM document_chunks
            ORDER BY embedding <=> %s::vector
            LIMIT %s;
        """, (embedding_str, embedding_str, top_k))

        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        if not rows:
            print("  No rows returned from database.")
            return []

        chunks = []
        for row in rows:
            content, source, similarity = row
            chunks.append({
                "content": content,
                "source": source,
                "similarity": round(float(similarity), 4)
            })
            print(f"  [{round(float(similarity), 4)}] {source}: {content[:80]}...")

        return chunks

    except Exception as e:
        print(f"  Retriever error: {repr(e)}")
        return []

if __name__ == "__main__":
    test_questions = [
        "What is a BREAKOUT signal?",
        "How do I open a position?",
        "What does the leaderboard endpoint return?"
    ]
    for q in test_questions:
        print(f"\n{'='*50}")
        results = retrieve(q)
        if not results:
            print(f"No results returned for: '{q}'")
        else:
            print(f"Top result for '{q}':")
            print(f"Source: {results[0]['source']}")
            print(f"Similarity: {results[0]['similarity']}")
            print(f"Content: {results[0]['content'][:300]}")
        time.sleep(1)