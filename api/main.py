import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from api.retriever import retrieve
from api.generator import generate_answer

load_dotenv()

app = FastAPI(title="UMX Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5174",
        "http://localhost:5173",
    ],
    allow_methods=["*"],
    allow_headers=["*"]
)

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str
    sources: list[str]
    chunk_count: int
    question: str

@app.get("/")
def root():
    return {"message": "UMX Assistant API is running"}

@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    question = req.question.strip()

    if not question:
        return AskResponse(
            answer="Please ask a question.",
            sources=[],
            chunk_count=0,
            question=question
        )

    chunks = retrieve(question)
    result = generate_answer(question, chunks)

    return AskResponse(
        answer=result["answer"],
        sources=result["sources"],
        chunk_count=result["chunk_count"],
        question=question
    )