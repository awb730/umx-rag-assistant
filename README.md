# UMExchange Assistant

A RAG-based documentation assistant for the UMExchange platform. Ask anything about how the platform works, the API endpoints, signal classification, investing mechanics, or the tech stack.

## How it works

1. Documentation corpus (README, API spec, explainer) is chunked and embedded using `OpenAI`
2. Embeddings are stored in Supabase pgvector
3. User questions are embedded and compared against stored chunks via cosine similarity
4. Top relevant chunks are passed to GPT-4o-mini with a strict grounding prompt
5. Answer is returned with with the sources GPT-4o-mini pulled from

## Stack

- FastAPI - API layer
- OpenAI - embeddings (text-embedding-3-small) + generation (gpt-4o-mini)
- Supabase pgvector - vector storage and similarity search
- React + Tailwind - frontend chat UI