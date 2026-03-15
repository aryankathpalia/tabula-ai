from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base
from sqlalchemy.dialects.postgresql import TSVECTOR


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)

    status = Column(String, default="uploaded")

    # Persisted Intelligence Fields
    overall_score = Column(Float, nullable=True)
    exposure_level = Column(String, nullable=True)
    risk_posture = Column(String, nullable=True)
    risk_concentration = Column(String, nullable=True)

    extracted_text = Column(Text, nullable=True)
    clause_analysis = Column(JSONB, nullable=True)

    analysis_confidence = Column(Float, nullable=True)
    summary = Column(Text, nullable=True)
    summary_status = Column(String, default="pending")
    masked_entities = Column(JSONB, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    search_vector = Column(TSVECTOR)

    chunks = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan"
    )