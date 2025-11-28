from __future__ import annotations

import logging
import os

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.agent.chat_agent import handle_message
from app.db import SessionLocal, create_tables


# --------------------------------------------------------------
# Logging setup (must be BEFORE FastAPI instantiation)
# --------------------------------------------------------------
log_level = os.getenv("INSTALILY_LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# --------------------------------------------------------------
# Pydantic Models
# --------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str
    conversation_snippet: str | None = None


class ChatResponse(BaseModel):
    reply: str
    metadata: dict | None = None


# --------------------------------------------------------------
# DB dependency
# --------------------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --------------------------------------------------------------
# Create/Initialize DB tables
# --------------------------------------------------------------
create_tables()


# --------------------------------------------------------------
# FastAPI app
# --------------------------------------------------------------
app = FastAPI(
    title="PartSelect Chat Agent",
    version="0.1.0",
    description="Refrigerator + Dishwasher parts assistant for PartSelect."
)


# --------------------------------------------------------------
# CORS
# --------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # For local dev / demo — safe for case study
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------------------
# Lifespan: optional warm-up steps
# --------------------------------------------------------------
@app.on_event("startup")
def startup_event():
    logger.info("🚀 PartSelect Agent is starting up...")
    # You can pre-warm RAG / DB here if desired:
    # from app.rag.vector_store import get_collection
    # get_collection("repairs")
    # get_collection("blogs")
    logger.info("Initialization complete.")


@app.on_event("shutdown")
def shutdown_event():
    logger.info("🛑 PartSelect Agent shutting down...")


# --------------------------------------------------------------
# Routes
# --------------------------------------------------------------
@app.get("/")
def root():
    return {
        "service": "PartSelect Chat Agent",
        "status": "online",
        "version": "0.1.0"
    }


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(payload: ChatRequest, db: Session = Depends(get_db)):
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    response_payload = handle_message(
        payload.message,
        db,
        conversation_snippet=payload.conversation_snippet
    )

    return ChatResponse.model_validate(response_payload)


@app.get("/health")
def health():
    return {"status": "ok"}
