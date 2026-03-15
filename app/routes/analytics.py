from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.document import Document

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard")
def get_dashboard_metrics(db: Session = Depends(get_db)):

   
    # Get latest version per document
   

    subquery = (
        db.query(
            Document.filename,
            func.max(Document.created_at).label("latest_created")
        )
        .group_by(Document.filename)
        .subquery()
    )

    latest_docs_query = (
        db.query(Document)
        .join(
            subquery,
            (Document.filename == subquery.c.filename) &
            (Document.created_at == subquery.c.latest_created)
        )
    )

    latest_docs = latest_docs_query.all()

   
    # Total Documents
   

    total_documents = len(latest_docs)

   
    # Average Risk Score
   

    scores = [doc.overall_score for doc in latest_docs if doc.overall_score]

    avg_score = sum(scores) / len(scores) if scores else 0

   
    # Exposure Distribution
   

    exposure_distribution = {
        "high": 0,
        "moderate": 0,
        "low": 0
    }

    for doc in latest_docs:

        if not doc.exposure_level:
            continue

        key = doc.exposure_level.lower().split()[0]

        if key in exposure_distribution:
            exposure_distribution[key] += 1

   
    # Recent Activity Table
   

    latest_docs_sorted = sorted(
        latest_docs,
        key=lambda d: d.overall_score or 0,
        reverse=True
    )[:10]

    recent_high_risk = [
        {
            "id": doc.id,
            "filename": doc.filename,
            "score": round(doc.overall_score or 0, 2),
            "exposure": doc.exposure_level
        }
        for doc in latest_docs_sorted
    ]

    return {
        "total_documents": total_documents,
        "average_risk_score": round(avg_score, 2),
        "exposure_distribution": exposure_distribution,
        "recent_high_risk_documents": recent_high_risk
    }