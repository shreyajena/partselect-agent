from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional

from .rag_query import query_collection

DEFAULT_COLLECTIONS = ("repairs", "blogs")


def _keyword_bonus(query: str, text: str) -> float:
    tokens = [t for t in re.split(r"[^a-z0-9]+", query.lower()) if len(t) > 3]
    if not tokens:
        return 0.0
    text_lower = text.lower()
    matches = sum(1 for token in tokens if token in text_lower)
    return matches / len(tokens)


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def retrieve_documents(
    query: str,
    *,
    top_k: int = 6,
    preferred_source: Optional[str] = None,
    collections: tuple[str, ...] = DEFAULT_COLLECTIONS,
) -> List[Dict[str, Any]]:
    candidates: List[Dict[str, Any]] = []
    for collection in collections:
        docs = query_collection(query=query, collection_name=collection, n_results=top_k)
        for doc in docs:
            item = dict(doc)
            item["source_collection"] = collection
            item["keyword_bonus"] = _keyword_bonus(query, doc.get("text", ""))
            candidates.append(item)

    if not candidates:
        return []

    selected: List[Dict[str, Any]] = []
    lambda_mult = 0.7
    source_bias = 0.1 if preferred_source else 0.0

    remaining = candidates[:]
    while remaining and len(selected) < top_k:
        best = None
        best_score = None
        for item in remaining:
            distance = item.get("distance")
            base_score = -(distance if distance is not None else 1.0)
            base_score += 0.2 * item.get("keyword_bonus", 0.0)
            if preferred_source and item.get("source_collection") == preferred_source:
                base_score += source_bias

            redundancy = 0.0
            if selected:
                redundancy = max(_similarity(item.get("text", ""), s.get("text", "")) for s in selected)

            mmr_score = lambda_mult * base_score - (1 - lambda_mult) * redundancy
            if best_score is None or mmr_score > best_score:
                best_score = mmr_score
                best = item

        if best is None:
            break
        selected.append(best)
        remaining.remove(best)

    return selected

