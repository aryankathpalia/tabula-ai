# app/routes/chat.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.models.document import Document
from app.services.retriever import retrieve_chunks_for_document
from app.services.llm_provider import generate_answer
from app.services.chat_memory import add_message, get_history


router = APIRouter(prefix="/chat", tags=["Chatbot"])


class ChatRequest(BaseModel):
    document_id: int
    conversation_id: str
    message: str


@router.post("/")
def chat(request: ChatRequest, db: Session = Depends(get_db)):

    # get document
    document = db.query(Document).filter(
        Document.id == request.document_id
    ).first()

    if not document:
        return {"error": "Document not found"}

    # retrieve relevant chunks
    chunks = retrieve_chunks_for_document(
        request.message,
        request.document_id,
        top_k=5,
        db=db
    )

    context = "\n\n".join(chunks)

    # conversation memory
    history = get_history(request.conversation_id)

    full_context = f"""
Conversation History:
{history}

Document Context:
{context}
"""

    # LLM answer
    result = generate_answer(
        query=request.message,
        context=full_context
    )

    # store memory
    add_message(request.conversation_id, "user", request.message)
    add_message(request.conversation_id, "assistant", result["direct_answer"])

    return result