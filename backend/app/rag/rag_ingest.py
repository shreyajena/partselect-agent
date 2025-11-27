"""
RAG ingestion utilities.

Usage examples:

    python -m app.rag.rag_ingest \
        --blogs data/blogs.json \
        --repairs data/repair_guides.json

You can also import the helpers directly for programmatic ingestion.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .rag_store import get_collection, upsert_document


def _log(message: str) -> None:
    """Lightweight console logging for ingestion scripts."""
    print(f"[rag_ingest] {message}")


def _log_document(doc_id: str, text: str, metadata: Dict[str, Any]) -> None:
    preview = text.strip().replace("\n", " ")[:140]
    _log(f"Indexing {doc_id} | preview=\"{preview}\" | metadata={metadata}")


# ---- Chunking helpers ------------------------------------------------------


def _split_into_chunks(
    text: str,
    max_chars: int = 800,
    overlap: int = 120,
) -> List[str]:
    """
    Simple sliding-window chunker on characters.

    - Keeps chunks reasonably small for DeepSeek
    - Adds overlap for better semantic continuity
    """
    text = (text or "").strip()
    if not text:
        return []

    if len(text) <= max_chars:
        return [text]

    chunks: List[str] = []
    start = 0
    length = len(text)

    while start < length:
        end = min(start + max_chars, length)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == length:
            break
        start = end - overlap  # overlap with previous

    return chunks


def _normalize_appliance_types(raw: Any) -> List[str]:
    """
    Normalizes appliance types to a list of lowercased strings.
    Handles strings ('Refrigerator; Dishwasher') and lists.
    """
    if raw is None:
        return []

    if isinstance(raw, list):
        return [str(x).strip().lower() for x in raw if str(x).strip()]

    # assume string
    seps = [";", ",", "|", "/"]
    s = str(raw)
    for sep in seps:
        s = s.replace(sep, ";")
    return [x.strip().lower() for x in s.split(";") if x.strip()]


def _normalize_tags(raw: Any) -> List[str]:
    """
    Normalizes symptom / tag fields to a list of strings.
    """
    if raw is None:
        return []

    if isinstance(raw, list):
        return [str(x).strip().lower() for x in raw if str(x).strip()]

    # assume string with separators
    seps = [";", ",", "|", "/"]
    s = str(raw)
    for sep in seps:
        s = s.replace(sep, ";")
    return [x.strip().lower() for x in s.split(";") if x.strip()]


def _metadata_list_value(values: List[str]) -> Optional[str]:
    """
    Chroma metadata only supports scalars, so convert lists to a
    semicolon-delimited lowercase string.
    """

    if not values:
        return None
    cleaned = [v.strip().lower() for v in values if v.strip()]
    return ";".join(cleaned) if cleaned else None


# ---- BLOG ingestion --------------------------------------------------------


def ingest_blogs(
    blogs: Iterable[Dict[str, Any]],
    collection_name: str = "blogs",
) -> None:
    """
    Ingest blog articles into the 'blogs' collection.

    Expected blog structure (aligned with your scraped JSON):

    {
      "id": "blog_dishwasher-cycle-guide",
      "title": "Guide to Dishwasher Cycles",
      "url": "https://www.partselect.com/...",
      "appliance_types": ["dishwasher"],               # optional
      "tags": ["cycle", "eco", "quick wash"],          # optional
      "sections": [
        { "heading": "What is a Rinse Cycle", "text": "..." },
        ...
      ]
    }
    """
    collection = get_collection(name=collection_name)
    total_blogs = 0
    total_chunks = 0

    for idx, blog in enumerate(blogs, start=1):
        blog_id = str(blog.get("id") or blog.get("slug") or blog.get("title"))
        title = blog.get("title", "").strip()
        url = blog.get("url")
        appliance_types = _normalize_appliance_types(
            blog.get("appliance_types")
        )
        tags = _normalize_tags(blog.get("tags"))

        sections: List[Dict[str, Any]] = blog.get("sections") or []

        appliance_meta = _metadata_list_value(appliance_types)
        tags_meta = _metadata_list_value(tags)

        for sec_idx, section in enumerate(sections):
            heading = (section.get("heading") or "").strip()
            text = (section.get("text") or "").strip()
            if not text:
                continue

            # chunk this section if needed
            chunks = _split_into_chunks(text)
            for chunk_idx, chunk in enumerate(chunks):
                doc_id = f"blog:{blog_id}::sec:{sec_idx}::chunk:{chunk_idx}"

                metadata: Dict[str, Any] = {
                    "source": "blog",
                    "blog_id": blog_id,
                    "title": title,
                    "url": url,
                    "section_index": sec_idx,
                    "section_heading": heading,
                    "chunk_index": chunk_idx,
                    "appliance_types": appliance_meta,
                    "tags": tags_meta,
                }

                # _log_document(doc_id, chunk, metadata)
                upsert_document(
                    doc_id=doc_id,
                    text=chunk,
                    metadata=metadata,
                    collection=collection,
                )
                total_chunks += 1

        total_blogs += 1
        if idx % 10 == 0:
            _log(f"Ingested {idx} blogs ({total_chunks} chunks so far).")

    _log(f"Finished ingesting blogs → {total_blogs} blogs, {total_chunks} chunks.")


def ingest_blogs_from_file(
    path: str | Path,
    collection_name: str = "blogs",
) -> None:
    """
    Convenience wrapper:
    - Loads blogs from a JSON file
    - Passes to ingest_blogs()
    """
    path = Path(path)
    _log(f"Loading blogs from {path}")
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # data can be { "blogs": [...] } or just [...]
    if isinstance(data, dict) and "blogs" in data:
        blogs = data["blogs"]
    else:
        blogs = data

    ingest_blogs(blogs=blogs, collection_name=collection_name)


# ---- REPAIR GUIDE ingestion -----------------------------------------------


def ingest_repairs(
    repairs: Iterable[Dict[str, Any]],
    collection_name: str = "repairs",
) -> None:
    """
    Ingest repair / troubleshooting guides into the 'repairs' collection.

    Expected structure (flexible):

    {
      "id": "repair_bosch-reset",
      "title": "How to Reset a Bosch Dishwasher",
      "url": "https://www.partselect.com/...",
      "appliance_type": "dishwasher",
      "symptom_tags": ["won't start", "error code", "stuck mid-cycle"],
      "steps": [
        { "title": "Soft Reset", "body": "..." },
        { "title": "Hard Reset", "body": "..." },
        ...
      ],
      "notes": "optional extra text"
    }

    The ingestion strategy:
    - Each step becomes one or more chunks
    - Metadata includes appliance_type + symptom_tags
    - Perfect to answer: "My Bosch dishwasher won't start, what should I try?"
    """
    collection = get_collection(name=collection_name)
    total_guides = 0
    total_chunks = 0

    for idx, guide in enumerate(repairs, start=1):
        guide_id = str(guide.get("id") or guide.get("slug") or guide.get("title"))
        title = (guide.get("title") or "").strip()
        url = guide.get("url")
        appliance_types = _normalize_appliance_types(
            guide.get("appliance_type") or guide.get("appliance_types")
        )
        symptom_tags = _normalize_tags(
            guide.get("symptom_tags") or guide.get("symptoms")
        )

        raw_steps: List[Dict[str, Any]] = guide.get("steps") or []
        raw_sections: List[Dict[str, Any]] = guide.get("sections") or []
        steps: List[Dict[str, Any]] = []

        if raw_steps:
            steps = raw_steps
        elif raw_sections:
            for section in raw_sections:
                steps.append(
                    {
                        "title": section.get("title"),
                        "body": section.get("body") or section.get("text"),
                    }
                )

        # Optional free-form notes text
        notes_text = (guide.get("notes") or "").strip()
        appliance_meta = _metadata_list_value(appliance_types)
        symptom_meta = _metadata_list_value(symptom_tags)

        # 1) Steps
        for step_idx, step in enumerate(steps):
            step_title = (step.get("title") or "").strip()
            body = (step.get("body") or step.get("text") or "").strip()
            if not body:
                continue

            chunks = _split_into_chunks(body)
            for chunk_idx, chunk in enumerate(chunks):
                doc_id = (
                    f"repair:{guide_id}::step:{step_idx}::chunk:{chunk_idx}"
                )

                metadata: Dict[str, Any] = {
                    "source": "repair_guide",
                    "guide_id": guide_id,
                    "title": title,
                    "url": url,
                    "step_index": step_idx,
                    "step_title": step_title,
                    "chunk_index": chunk_idx,
                    "appliance_types": appliance_meta,
                    "symptom_tags": symptom_meta,
                }

                _log_document(doc_id, chunk, metadata)
                upsert_document(
                    doc_id=doc_id,
                    text=chunk,
                    metadata=metadata,
                    collection=collection,
                )
                total_chunks += 1

        # 2) Optional notes as a separate chunk
        if notes_text:
            chunks = _split_into_chunks(notes_text)
            for chunk_idx, chunk in enumerate(chunks):
                doc_id = f"repair:{guide_id}::notes::chunk:{chunk_idx}"
                metadata = {
                    "source": "repair_guide",
                    "guide_id": guide_id,
                    "title": title,
                    "url": url,
                    "section": "notes",
                    "chunk_index": chunk_idx,
                    "appliance_types": appliance_meta,
                    "symptom_tags": symptom_meta,
                }
                _log_document(doc_id, chunk, metadata)
                upsert_document(
                    doc_id=doc_id,
                    text=chunk,
                    metadata=metadata,
                    collection=collection,
                )
                total_chunks += 1

        total_guides += 1
        if idx % 10 == 0:
            _log(f"Ingested {idx} repair guides ({total_chunks} chunks so far).")

    _log(f"Finished ingesting repairs → {total_guides} guides, {total_chunks} chunks.")

def ingest_repairs_from_file(
    path: str | Path,
    collection_name: str = "repairs",
) -> None:
    """
    Convenience wrapper:
    - Loads repair guides from a JSON file
    - Passes to ingest_repairs()
    """
    path = Path(path)
    _log(f"Loading repairs from {path}")
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict) and "repairs" in data:
        repairs = data["repairs"]
    else:
        repairs = data

    ingest_repairs(repairs=repairs, collection_name=collection_name)

def main() -> None:
    parser = argparse.ArgumentParser(description="RAG ingestion utility.")
    parser.add_argument(
        "--blogs",
        type=str,
        default="data/blogs.json",
        help="Path to blogs JSON (omit or set empty string to skip).",
    )
    parser.add_argument(
        "--repairs",
        type=str,
        default="data/repair_guides.json",
        help="Path to repair guides JSON (omit or set empty string to skip).",
    )
    parser.add_argument(
        "--skip-blogs",
        action="store_true",
        help="Skip blog ingestion even if --blogs is provided.",
    )
    parser.add_argument(
        "--skip-repairs",
        action="store_true",
        help="Skip repair ingestion even if --repairs is provided.",
    )
    args = parser.parse_args()

    ran_any = False
    if args.blogs and not args.skip_blogs:
        ingest_blogs_from_file(args.blogs)
        ran_any = True
    if args.repairs and not args.skip_repairs:
        ingest_repairs_from_file(args.repairs)
        ran_any = True

    if not ran_any:
        parser.error("Nothing ingested. Provide --blogs/--repairs or remove skip flags.")


if __name__ == "__main__":
    main()
