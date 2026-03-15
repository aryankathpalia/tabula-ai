from fastapi import APIRouter, UploadFile, Depends

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.document import Document
from app.schemas.document import DocumentOut
from app.services.storage import save_file
from app.services.extractor import extract_text
from app.services.chunker import chunk_text
from app.models.chunk import DocumentChunk
from app.services.embeddings import embed_text
from app.services.transformer_classifier import get_classifier
from sqlalchemy import text


from fastapi import HTTPException
from fastapi.responses import FileResponse
import os
from app.services.risk_intelligence.summary_builder import build_enterprise_summary
from app.services.storage_supabase import upload_file

from fastapi import BackgroundTasks


from fastapi.responses import StreamingResponse
import asyncio
import json


router = APIRouter(prefix="/documents", tags=["Documents"])


import re




from collections import defaultdict


classifier = get_classifier()






def clean_text(text: str):
    text = re.sub(r'Page\s+\d+\s+of\s+\d+', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\n\d+\n', '\n', text)
    text = re.sub(r'\n+', '\n', text)
    return text.strip()



def normalize_tokens(text: str):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s]', '', text)
    return text.lower().strip().split()


def token_overlap_ratio(a_tokens, b_tokens):
    set_a = set(a_tokens)
    set_b = set(b_tokens)
    intersection = set_a.intersection(set_b)
    return len(intersection) / max(len(set_a), 1)



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

        # Skip list markers like "a." or "1."
        if re.match(r'^[a-zA-Z]\.$', line.strip()):
            continue

        if re.match(r'^\d+\.$', line.strip()):
            continue


        # sentence end
        if line.endswith("."):
            if len(buffer.strip()) > 40:
                clauses.append(buffer.strip())
            buffer = ""

    # leftover
    if len(buffer.strip()) > 40:
        clauses.append(buffer.strip())

    return clauses


import re




def locate_clause_bbox(clause, pages_layout):

    clause_tokens = normalize_tokens(clause)

    best_match = None
    best_score = 0

    for page in pages_layout:

        page_words = page["words"]

        page_tokens = [
            normalize_tokens(w["text"])[0]
            for w in page_words
            if normalize_tokens(w["text"])
        ]

        window_size = len(clause_tokens)

        for i in range(0, len(page_tokens) - window_size + 1):

            window_tokens = page_tokens[i:i + window_size]

            overlap = token_overlap_ratio(clause_tokens, window_tokens)

            if overlap > best_score:
                best_score = overlap
                best_match = (page, page_words[i:i + window_size])

    if best_match and best_score > 0.8:

        page, matched_words = best_match

        lines = defaultdict(list)

        for w in matched_words:
            line_key = round(w["bbox"][1], 1)
            lines[line_key].append(w)

        line_boxes = []

        for line_words in lines.values():
            min_x = min(w["bbox"][0] for w in line_words)
            min_y = min(w["bbox"][1] for w in line_words)
            max_x = max(w["bbox"][2] for w in line_words)
            max_y = max(w["bbox"][3] for w in line_words)

            line_boxes.append((min_x, min_y, max_x, max_y))

        min_x = min(box[0] for box in line_boxes)
        min_y = min(box[1] for box in line_boxes)
        max_x = max(box[2] for box in line_boxes)
        max_y = max(box[3] for box in line_boxes)

        pdfjs_y = page["height"] - max_y

        bbox = {
            "x": min_x,
            "y": pdfjs_y,
            "width": max_x - min_x,
            "height": max_y - min_y
        }

        return page["page_number"], bbox

    return None, None



def retrieve_candidate_chunks(db, document_id, query_embeddings):

    results = []

    for emb in query_embeddings:

        rows = db.execute(
            text("""
            SELECT text
            FROM document_chunks
            WHERE document_id = :doc_id
            ORDER BY embedding <-> CAST(:embedding AS vector)
            LIMIT 15
            """),
            {
                "doc_id": document_id,
                "embedding": emb
            }
        ).fetchall()

        for r in rows:
            results.append(r.text)

    return list(set(results))




def find_similar_chunk(db, document_id: int, clause_embedding):

    result = db.execute(
        text("""
        SELECT id, text
        FROM document_chunks
        WHERE document_id = :doc_id
        ORDER BY embedding <-> CAST(:embedding AS vector)
        LIMIT 3
        """),
        {
            "doc_id": document_id,
            "embedding": clause_embedding
        }
    ).fetchall()

    return result


def process_summary_pipeline(document_id: int, local_path: str):

    from app.core.database import SessionLocal

    db = SessionLocal()

    doc = db.query(Document).filter(Document.id == document_id).first()

    if not doc:
        db.close()
        return

    # mark summary processing
    doc.summary_status = "processing"
    db.commit()

    extracted = extract_text(local_path)
    document_text = extracted["full_text"]
    pages_layout = extracted.get("pages", [])


        # ----- STEP 1: create chunk embeddings FIRST -----

    doc.embedding_status = "processing"
    db.commit()

    chunks = chunk_text(document_text, max_chars=800)

    filtered_chunks = [
        chunk for chunk in chunks
        if len(chunk.strip()) >= 50
    ]

    embeddings = embed_text(filtered_chunks)

    for index, (chunk, embedding) in enumerate(zip(filtered_chunks, embeddings)):

        db_chunk = DocumentChunk(
            document_id=doc.id,
            chunk_index=index,
            text=chunk,
            embedding=embedding
        )

        db.add(db_chunk)

    db.commit()

    doc.embedding_status = "completed"
    db.commit()


    page_texts = []

    for page in pages_layout[:3]:

        page_words = page["words"]

        page_text = " ".join(w["text"] for w in page_words)

        page_texts.append((page, page_words, page_text))



    from app.services.pii_masker import mask_pii
    masked_text, mapping = mask_pii(document_text)

    doc.extracted_text = masked_text
    doc.masked_entities = mapping
    db.commit()

    # ---------- VECTOR SEARCH FIRST ----------


    clauses = split_into_clauses(document_text)

    grouped_results = defaultdict(list)
    seen_clauses = set()

    for clause in clauses:

        clause_clean = clause.strip()

        if len(clause_clean) < 40:
            continue

        # prevent duplicates
        clause_key = clause_clean.lower()

        if clause_key in seen_clauses:
            continue

        seen_clauses.add(clause_key)

        prediction = classifier.predict(clause_clean)

        if prediction["confidence"] < 0.85:
            continue


        page_number, bbox = locate_clause_bbox(clause, pages_layout)

        grouped_results[prediction["label"]].append({
            "clause_text": clause,
            "confidence": prediction["confidence"],
            "page": page_number,
            "bbox": bbox
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


# ---------- SUMMARY ----------

    if doc.clause_analysis:

        summary_output = build_enterprise_summary(doc.clause_analysis)

        doc.overall_score = summary_output["overall_score"]
        doc.exposure_level = summary_output["exposure_level"]
        doc.risk_posture = summary_output["risk_posture"]
        doc.risk_concentration = summary_output["risk_concentration"]
        doc.summary = summary_output["summary_markdown"]

    else:
        doc.summary = "No significant risk clauses were detected in this document."
        doc.overall_score = 0
        doc.exposure_level = "Low"
        doc.risk_posture = "Neutral"
        doc.risk_concentration = "None" 


    doc.summary_status = "completed"
    doc.status = "processed"   
    db.commit()

    db.close()




@router.post("/", response_model=DocumentOut)
def upload_document(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):

    # save locally for processing
    local_path = save_file(file)

    # upload to supabase for permanent storage
    public_url = upload_file(file)

    doc = Document(
        filename=file.filename,
        content_type=file.content_type,
        storage_path=public_url,
        status="processing"
    )

    db.add(doc)
    db.commit()
    db.refresh(doc)

    from sqlalchemy import text

    db.execute(
        text("""
            UPDATE documents
            SET search_vector =
                to_tsvector('english', coalesce(filename,''))
            WHERE id = :doc_id
        """),
        {"doc_id": doc.id}
    )

    db.commit()

    # RUN FULL PIPELINE IN BACKGROUND
    background_tasks.add_task(process_summary_pipeline, doc.id, local_path)

    return doc





@router.get("/{document_id}", response_model=DocumentOut)
def get_document(document_id: int, db: Session = Depends(get_db)):

        document = db.query(Document).filter(Document.id == document_id).first()

        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        return document



@router.get("/{document_id}/file")
def get_document_file(document_id: int, db: Session = Depends(get_db)):

    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    from fastapi.responses import RedirectResponse

    return RedirectResponse(document.storage_path)
 


@router.get("/{document_id}/summary-stream")
async def summary_stream(document_id: int):

    from app.core.database import SessionLocal

    async def event_stream():

        db = SessionLocal()

        while True:

            doc = db.query(Document).filter(Document.id == document_id).first()

            if not doc:
                yield f"data: {json.dumps({'error': 'not_found'})}\n\n"
                break

            payload = {
                "summary_status": doc.summary_status,
                "embedding_status": getattr(doc, "embedding_status", None),
                "summary": doc.summary,
                "overall_score": doc.overall_score,
                "exposure_level": doc.exposure_level,
                "risk_posture": doc.risk_posture
            }

            yield f"data: {json.dumps(payload)}\n\n"

            if doc.summary_status == "completed":
                break

            await asyncio.sleep(2)

        db.close()

    return StreamingResponse(event_stream(), media_type="text/event-stream")


from sqlalchemy import func

@router.get("/", response_model=list[DocumentOut])
def list_documents(db: Session = Depends(get_db)):

    subquery = (
        db.query(
            Document.filename,
            func.max(Document.created_at).label("latest_created")
        )
        .group_by(Document.filename)
        .subquery()
    )

    latest_docs = (
        db.query(Document)
        .join(
            subquery,
            (Document.filename == subquery.c.filename) &
            (Document.created_at == subquery.c.latest_created)
        )
        .order_by(Document.created_at.desc())
        .all()
    )

    return latest_docs


from app.services.risk_intelligence.summary_builder import build_enterprise_summary


@router.get("/{document_id}/local-summary")
def get_local_summary(document_id: int, db: Session = Depends(get_db)):

    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # summary not ready
    if document.summary_status != "completed":
        return {"status": "processing"}

    return {
        "status": "completed",
        "summary": document.summary,
        "overall_score": document.overall_score,
        "exposure_level": document.exposure_level,
        "risk_posture": document.risk_posture,
        "risk_concentration": document.risk_concentration
    }


@router.delete("/{doc_id}")
def delete_document(doc_id: int, db: Session = Depends(get_db)):

    doc = db.query(Document).filter(Document.id == doc_id).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    db.delete(doc)
    db.commit()

    return {"success": True}