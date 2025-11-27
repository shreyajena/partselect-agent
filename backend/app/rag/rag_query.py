# backend/app/rag_query.py

"""
Query helpers for RAG:
- Query specific collections (blogs, repairs)
- Return normalized results
- Build LLM-ready context for DeepSeek
"""

from __future__ import annotations

import argparse
from typing import Any, Dict, List, Optional

from .rag_store import get_collection


def query_collection(
    query: str,
    collection_name: str,
    n_results: int = 6,
    where: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Run a semantic search against a given collection and return
    structured results.

    Returns:
        [
          {
            "id": "blog:...::chunk:0",
            "text": "chunk text",
            "metadata": {...},
            "distance": 0.123
          },
          ...
        ]
    """
    col = get_collection(name=collection_name)

    results = col.query(
        query_texts=[query],
        n_results=n_results,
        where=where,
    )

    ids = results.get("ids", [[]])[0]
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    normalized: List[Dict[str, Any]] = []
    for i, doc_id in enumerate(ids):
        if doc_id is None:
            continue
        normalized.append(
            {
                "id": doc_id,
                "text": docs[i],
                "metadata": metas[i],
                "distance": distances[i],
            }
        )

    return normalized


def query_blogs(
    query: str,
    appliance_filter: Optional[str] = None,
    n_results: int = 6,
) -> List[Dict[str, Any]]:
    """
    Shortcut for blog search.

    appliance_filter examples:
      - "dishwasher"
      - "refrigerator"
    """
    where = None
    if appliance_filter:
        where = {
            "appliance_types": {
                "$contains": appliance_filter.lower()
            }
        }

    return query_collection(
        query=query,
        collection_name="blogs",
        n_results=n_results,
        where=where,
    )


def query_repairs(
    query: str,
    symptom_filter: Optional[str] = None,
    appliance_filter: Optional[str] = None,
    n_results: int = 6,
) -> List[Dict[str, Any]]:
    """
    Shortcut for repair guide search.

    You can optionally filter by:
      - symptom_filter: "won't start", "not draining"
      - appliance_filter: "dishwasher", "refrigerator"
    """
    where: Dict[str, Any] = {}
    if symptom_filter:
        where.setdefault("symptom_tags", {})["$contains"] = symptom_filter.lower()
    if appliance_filter:
        where.setdefault("appliance_types", {})["$contains"] = appliance_filter.lower()

    if not where:
        where_clause = None
    else:
        # simple AND of conditions
        where_clause = where

    return query_collection(
        query=query,
        collection_name="repairs",
        n_results=n_results,
        where=where_clause,
    )


def build_context_block(
    results: List[Dict[str, Any]],
    max_chars: int = 4000,
) -> str:
    """
    Turn a list of RAG results into a single string you can feed to DeepSeek.

    It keeps them compact but nicely labeled.
    """
    lines: List[str] = []
    current_len = 0

    for r in results:
        meta = r.get("metadata") or {}
        source = meta.get("source", "unknown")
        title = meta.get("title") or meta.get("section_heading") or ""
        url = meta.get("url") or ""
        prefix = f"[{source}] {title}".strip()
        if url:
            prefix += f" ({url})"

        block = f"{prefix}\n{r['text'].strip()}\n"
        if current_len + len(block) > max_chars:
            break

        lines.append(block)
        current_len += len(block)

    return "\n---\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ad-hoc RAG query tester.")
    parser.add_argument("query", help="Natural language query.")
    parser.add_argument(
        "--collection",
        choices=["blogs", "repairs"],
        default="blogs",
        help="Which collection to search.",
    )
    parser.add_argument(
        "--appliance",
        help="Optional appliance filter (e.g., dishwasher, refrigerator).",
    )
    parser.add_argument(
        "--symptom",
        help="Optional symptom filter (repairs only).",
    )
    parser.add_argument(
        "--results",
        type=int,
        default=4,
        help="Number of matches to return.",
    )
    parser.add_argument(
        "--max-context",
        type=int,
        default=1500,
        help="Max characters for the preview context block.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print metadata for each match.",
    )
    args = parser.parse_args()

    if args.collection == "blogs":
        matches = query_blogs(
            query=args.query,
            appliance_filter=args.appliance,
            n_results=args.results,
        )
    else:
        matches = query_repairs(
            query=args.query,
            appliance_filter=args.appliance,
            symptom_filter=args.symptom,
            n_results=args.results,
        )

    print(f"Returned {len(matches)} results from {args.collection}.")
    for idx, match in enumerate(matches, start=1):
        meta = match.get("metadata") or {}
        distance = match.get("distance")
        dist_str = f"{distance:.4f}" if isinstance(distance, (int, float)) else "n/a"
        print(f"[{idx}] id={match['id']} distance={dist_str}")
        print(f"     text={match['text'][:120].strip()}...")
        if args.verbose:
            print(f"     metadata={meta}")

    if matches:
        print("\nContext block preview:\n")
        print(build_context_block(matches, max_chars=args.max_context))


if __name__ == "__main__":
    main()
