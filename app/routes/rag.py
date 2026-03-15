from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.retriever import retrieve_chunks_for_document
from app.services.llm_provider import generate_answer

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/answer")
def rag_answer(query: str, top_k: int = 5, db: Session = Depends(get_db)):
    chunks = retrieve_chunks_for_document(query, top_k, db)

    if not chunks:
        return {
            "query": query,
            "analysis": "No relevant content found.",
            "retrieved_chunks": 0
        }

    context = "\n\n".join([c["text"] for c in chunks])

    structured_answer = generate_answer(query, context)

    return {
        "query": query,
        "retrieved_chunks": len(chunks),
        "analysis": structured_answer
    }
