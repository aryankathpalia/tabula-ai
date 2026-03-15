from fastapi import APIRouter, Depends, HTTPException, UploadFile, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from collections import defaultdict
import re

from app.core.database import get_db
from app.models.document import Document
from app.models.chunk import DocumentChunk

from app.services.storage import save_file
from app.services.extractor import extract_text
from app.services.chunker import chunk_text
from app.services.embeddings import embed_text
from app.services.transformer_classifier import get_classifier
from app.services.risk_intelligence.summary_builder import build_enterprise_summary

from app.services.retriever import retrieve_chunks_for_document
from app.services.reranker import rerank_chunks
from app.services.llm_provider import generate_answer
from app.services.storage_supabase import upload_file

router = APIRouter(prefix="/documents", tags=["Document Chat"])


class ChatRequest(BaseModel):
    question: str
    history: list | None = []  # Optional conversation history for context

    
# Helper functions (same as main pipeline)
    

def clean_text(text: str):
    text = re.sub(r'Page\s+\d+\s+of\s+\d+', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\n\d+\n', '\n', text)
    text = re.sub(r'\n+', '\n', text)
    return text.strip()


def split_into_clauses(text: str):

    text = clean_text(text)

    lines = text.split("\n")

    clauses = []
    buffer = ""

    for line in lines:

        line = line.strip()
        if not line:
            continue

        buffer += " " + line

        if line.endswith("."):
            if len(buffer.strip()) > 40:
                clauses.append(buffer.strip())
            buffer = ""

    if len(buffer.strip()) > 40:
        clauses.append(buffer.strip())

    return clauses


    
# BACKGROUND RISK PIPELINE
    

def run_risk_pipeline(document_id: int):

    from app.core.database import SessionLocal
    db = SessionLocal()

    doc = db.query(Document).filter(Document.id == document_id).first()

    if not doc:
        return

    clauses = split_into_clauses(doc.extracted_text)

    grouped_results = defaultdict(list)

    for clause in clauses:

        classifier = get_classifier()
        prediction = classifier.predict(clause)

        if prediction["confidence"] <= 0.85:
            continue

        grouped_results[prediction["label"]].append({
            "clause_text": clause,
            "confidence": prediction["confidence"]
        })

    all_confidences = [
        item["confidence"]
        for items in grouped_results.values()
        for item in items
    ]

    analysis_confidence = (
        sum(all_confidences) / len(all_confidences)
        if all_confidences else 0
    )

    doc.clause_analysis = dict(grouped_results)
    doc.analysis_confidence = round(analysis_confidence * 100, 2)
    doc.status = "processed"

    if doc.clause_analysis:

        summary_output = build_enterprise_summary(doc.clause_analysis)

        doc.overall_score = summary_output["overall_score"]
        doc.exposure_level = summary_output["exposure_level"]
        doc.risk_posture = summary_output["risk_posture"]
        doc.risk_concentration = summary_output["risk_concentration"]
        doc.summary = summary_output["summary_markdown"]
        doc.summary_status = "completed"

    db.commit()
    db.close()


    
# CHAT UPLOAD (FAST INGESTION)
    

@router.post("/chat-upload")
def upload_document_for_chat(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):

    local_path = save_file(file)
    public_url = upload_file(file)

    extracted = extract_text(local_path)
    document_text = extracted["full_text"]

    doc = Document(
        filename=file.filename,
        content_type=file.content_type,
        storage_path=public_url,
        extracted_text=document_text,
        status="processing"
    )

    db.add(doc)
    db.commit()
    db.refresh(doc)

    # chunk + embeddings
    chunks = chunk_text(document_text, max_chars=800)

    for index, chunk in enumerate(chunks):

        if len(chunk.strip()) < 50:
            continue

        embedding = embed_text(chunk)[0]

        db_chunk = DocumentChunk(
            document_id=doc.id,
            chunk_index=index,
            text=chunk,
            embedding=embedding
        )

        db.add(db_chunk)

    db.commit()

    # run scoring async
    background_tasks.add_task(run_risk_pipeline, doc.id)

    return {
        "document_id": doc.id,
        "filename": doc.filename
    }


    
# CHAT WITH DOCUMENT (RAG)
    

@router.post("/{document_id}/chat")
def chat_with_document(
    document_id: int,
    request: ChatRequest,
    db: Session = Depends(get_db)
):

    document = db.query(Document).filter(
        Document.id == document_id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    candidates = retrieve_chunks_for_document(
        query=request.question,
        document_id=document_id,
        top_k=20,
        db=db
    )

    top_chunks = rerank_chunks(
        query=request.question,
        chunks=candidates,
        top_k=5
    )

    context = "\n\n".join([c["text"] for c in top_chunks])
    context = context[:6000]

    history_text = ""

    if request.history:
        for msg in request.history:
            role = msg.get("role")
            content = msg.get("content")

            if role == "user":
                history_text += f"User: {content}\n"
            else:
                history_text += f"Assistant: {content}\n"

    answer = generate_answer(
        query=request.question,
        context=context,
        history=history_text
    )

    return {
        "question": request.question,
        "answer": answer,
        "sources": top_chunks
    }