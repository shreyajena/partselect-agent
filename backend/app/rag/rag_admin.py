# backend/app/rag_admin.py

"""
Admin helpers for Chroma:
- Reset (delete) a collection
- List collections

Used during development / case study iterations.
"""

from __future__ import annotations

import argparse
from functools import lru_cache
from typing import List

import chromadb

from ..config import settings


@lru_cache(maxsize=1)
def _admin_client() -> chromadb.ClientAPI:
    """
    Separate admin-level client.

    We don't need embeddings here; we only care about deleting / listing
    collections in the same directory as rag_store.py.
    """
    settings.chroma_dir.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(settings.chroma_dir))


def reset_collection(name: str) -> None:
    """
    Deletes a collection and all its vectors.

    Example usage in a dev script:

        from app.rag_admin import reset_collection
        reset_collection("blogs")
        reset_collection("repairs")
    """
    client = _admin_client()
    try:
        client.delete_collection(name)
    except Exception as e:
        # Safe-ish: collection may not exist yet; that's ok during dev
        print(f"[rag_admin] Could not delete collection '{name}': {e}")


def list_collections() -> List[str]:
    """
    Returns a simple list of collection names for debugging.
    """
    client = _admin_client()
    cols = client.list_collections()
    return [c.name for c in cols]


def main() -> None:
    parser = argparse.ArgumentParser(description="Chroma collection admin helpers.")
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available collections.",
    )
    parser.add_argument(
        "--reset",
        action="append",
        metavar="NAME",
        help="Delete a collection. Can be passed multiple times.",
    )
    args = parser.parse_args()

    if args.reset:
        for name in args.reset:
            print(f"[rag_admin] Resetting '{name}'")
            reset_collection(name)

    if args.list or not args.reset:
        print("Collections:", list_collections())


if __name__ == "__main__":
    main()
