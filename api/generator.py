import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

SIMILARITY_THRESHOLD = 0.3

SYSTEM_PROMPT = """You are the UMExchange documentation assistant. 
UMExchange is a platform that applies quantitative finance concepts to underground rap streaming data — treating artists like financial assets with momentum signals, and letting users open LONG/SHORT positions on artist growth.

You answer questions strictly based on the provided documentation context. 

Rules:
- Only use information from the provided context chunks
- If the context does not contain enough information to answer, say "I don't have enough information in the documentation to answer that question." — never make things up
- Always be specific and technical when the question calls for it
- Keep answers concise but complete
- When referencing specific endpoints, signal types, or numbers, quote them exactly as they appear in the docs
- Do NOT list sources or context references at the end of your answer — sources are shown separately in the UI"""

def generate_answer(question: str, chunks: list[dict]) -> dict:
    """
    Generate a grounded answer from retrieved chunks.
    Returns the answer text and sources used.
    """

    # Filters out irrevalant chunks that are not similar to the question
    relevant_chunks = [c for c in chunks if c["similarity"] >= SIMILARITY_THRESHOLD]


    if not relevant_chunks:
        return {
            "answer": "I don't have enough information in the documentation to answer that question. Try rephrasing or asking about a specific feature, endpoint, or concept.",
            "sources": [],
            "chunk_count": 0
        }
    
    # Build context string from chunks
    context = ""
    for i, chunk in enumerate(relevant_chunks):
        context += f"\n--- Context {i + 1} (from {chunk['source']}) ---\n"
        context += chunk["content"]
        context += "\n"

    # Build the user message
    user_message = f"""Documentation context:
{context}

Question: {question}

Answer based strictly on the documentation context above."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=0.1,  # Low temperature for factual, consistent answers
        max_tokens=600
    )

    answer = response.choices[0].message.content

    # Collect unique sources
    sources = list(set(c["source"] for c in relevant_chunks))

    return {
        "answer": answer,
        "sources": sources,
        "chunk_count": len(relevant_chunks)
    }


if __name__ == "__main__":
    from api.retriever import retrieve

    test_questions = [
        "What is a BREAKOUT signal?",
        "How do I open a position?",
        "What does the leaderboard endpoint return?",
        "What happens when I close a position?",
        "How much does the Pro credit bundle cost?"
    ]

    for question in test_questions:
        print(f"\n{'='*60}")
        print(f"Q: {question}")
        chunks = retrieve(question)
        result = generate_answer(question, chunks)
        print(f"\nANSWER: {result['answer']}")
        print(f"\nSources: {', '.join(result['sources'])}")
        print(f"Chunks used: {result['chunk_count']}")