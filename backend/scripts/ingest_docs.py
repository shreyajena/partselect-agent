"""
CLI utility to populate the Chroma vector store with repair guides and blogs.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, Iterable

from app.config import settings
from backend.app.rag.rag_store import get_collection, upsert_document


REPAIR_JSON = settings.data_dir / "repair_guides.json"
BLOGS_JSON = settings.data_dir / "blogs.json"


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "section"


def _load_json(path: Path) -> Iterable[Dict]:
    if not path.exists():
        raise FileNotFoundError(f"JSON data not found at {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def _index_repair_guides(collection) -> int:
    guides = _load_json(REPAIR_JSON)
    count = 0
    for guide in guides:
        sections = guide.get("sections", [])
        for section in sections:
            doc_id = "repair_{appliance}_{symptom}_{section}".format(
                appliance=_slugify(guide.get("appliance", "appliance")),
                symptom=_slugify(guide.get("symptom", "symptom")),
                section=_slugify(section.get("title", "section")),
            )
            metadata = {
                "type": "repair_section",
                "appliance": guide.get("appliance"),
                "symptom": guide.get("symptom"),
                "title": guide.get("title"),
                "section_title": section.get("title"),
                "source_url": guide.get("url"),
            }
            upsert_document(doc_id, section.get("text", ""), metadata, collection=collection)
            count += 1
    return count


def _index_blogs(collection) -> int:
    blogs = _load_json(BLOGS_JSON)
    count = 0
    for blog in blogs:
        sections = blog.get("sections", [])
        appliance = blog.get("appliance")  # optional field
        for section in sections:
            doc_id = "blog_{blog_id}_{section}".format(
                blog_id=_slugify(blog.get("id", "blog")),
                section=_slugify(section.get("heading", "section")),
            )
            metadata = {
                "type": "blog_section",
                "appliance": appliance,
                "symptom": None,
                "title": blog.get("title"),
                "section_title": section.get("heading"),
                "source_url": blog.get("url"),
            }
            upsert_document(doc_id, section.get("text", ""), metadata, collection=collection)
            count += 1
    return count


def main() -> None:
    collection = get_collection()
    repair_count = _index_repair_guides(collection)
    blog_count = _index_blogs(collection)
    print(f"Indexed {repair_count} repair sections and {blog_count} blog sections into Chroma.")


if __name__ == "__main__":
    main()

