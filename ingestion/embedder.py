import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

def embed_text(text: str) -> list[float]:
    """Convert a piece of text into a 1536-dimension embedding vector."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    embedding = response.data[0].embedding
    print(f"  Embedding length: {len(embedding)}")
    return embedding

def embed_chunks(chunks: list[dict]) -> list[dict]:
    embedded = []
    for i, chunk in enumerate(chunks):
        print(f"Embedding chunk {i + 1}/{len(chunks)}: {chunk['source']}...")
        embedding = embed_text(chunk["content"])
        embedded.append({
            "content": chunk["content"],
            "source": chunk["source"],
            "embedding": embedding
        })
    return embedded