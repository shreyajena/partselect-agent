"""
Utility helpers for interacting with the local Chroma vector store.
"""

from functools import lru_cache
from typing import Any, Dict, Optional

import chromadb
from chromadb.api.models.Collection import Collection
from chromadb.utils import embedding_functions

from ..config import settings


def _build_embedding_function():
    """
    Prefer a small sentence transformer model, but gracefully fall back to
    Chroma's deterministic default when the dependency is unavailable.
    """

    try:
        return embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
    except Exception:
        return embedding_functions.DefaultEmbeddingFunction()


_embedding_function = _build_embedding_function()


@lru_cache(maxsize=1)
def _client() -> chromadb.ClientAPI:
    settings.chroma_dir.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(settings.chroma_dir))


def get_collection(name: Optional[str] = None) -> Collection:
    collection_name = name or settings.chroma_collection
    return _client().get_or_create_collection(
        name=collection_name,
        embedding_function=_embedding_function,
    )


def upsert_document(doc_id: str, text: str, metadata: Dict[str, Any], collection: Optional[Collection] = None) -> None:
    """
    Persist (or overwrite) a document chunk in the configured Chroma collection.
    """

    if not text:
        return

    col = collection or get_collection()
    col.upsert(
        ids=[doc_id],
        documents=[text],
        metadatas=[metadata],
    )

