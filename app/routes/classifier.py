from fastapi import APIRouter
from pydantic import BaseModel

from app.services.transformer_classifier import get_classifier

router = APIRouter()

class DocumentRequest(BaseModel):
    text: str


def split_into_clauses(text: str):
    return [c.strip() for c in text.split(".") if c.strip()]


@router.post("/analyze")
def analyze_document(request: DocumentRequest):

    clauses = split_into_clauses(request.text)
    results = []

    for clause in clauses:
        prediction = get_classifier.predict(clause)

        results.append({
            "clause_text": clause[:300],
            "label": prediction["label"],
            "confidence": prediction["confidence"]
        })

    return {"results": results}
