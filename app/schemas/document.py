from pydantic import BaseModel
from typing import Dict, List
from datetime import datetime
from typing import Optional, Dict




class ClauseItem(BaseModel):
    clause_text: str
    confidence: float
    page: Optional[int] = None
    bbox: Optional[Dict] = None



class DocumentOut(BaseModel):
    id: int
    filename: str
    content_type: str
    storage_path: str
    status: str
    created_at: datetime

    clause_analysis: Optional[Dict[str, List[ClauseItem]]] = None
    analysis_confidence: Optional[float] = None
    masked_entities: Optional[Dict[str, str]] = None

    summary: Optional[str] = None
    summary_status: Optional[str] = None

    class Config:
        from_attributes = True
