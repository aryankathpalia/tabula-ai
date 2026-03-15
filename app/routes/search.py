from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.retriever import retrieve_documents
from pydantic import BaseModel


router = APIRouter(prefix="/search", tags=["Search"])


class SearchRequest(BaseModel):
    query: str
    top_k: int = 10


@router.post("/")
def search_documents(request: SearchRequest, db: Session = Depends(get_db)):

    results = retrieve_documents(request.query, request.top_k, db)

    return {
        "query": request.query,
        "total_results": len(results),
        "results": results
    }