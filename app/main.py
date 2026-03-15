from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.routes import documents
from app.routes import rag
from app.routes.search import router as search_router
from app.routes import classifier
from app.routes.analytics import router as analytics_router
from app.routes import chat
from app.routes import document_chat

from app.services.transformer_classifier import get_classifier



app = FastAPI(title="Document Intelligence API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://tabula-ai.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# File storage
os.makedirs("uploaded_files", exist_ok=True)
app.mount("/files", StaticFiles(directory="uploaded_files"), name="files")

# Routers
app.include_router(documents.router)
app.include_router(rag.router)
app.include_router(search_router)
app.include_router(classifier.router)
app.include_router(analytics_router)
app.include_router(chat.router)
app.include_router(document_chat.router)


@app.on_event("startup")
def load_models():
    get_classifier()

# Health check
@app.get("/")
def health():
    return {"status": "Tabula AI backend running"}