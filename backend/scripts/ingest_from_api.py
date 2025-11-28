"""
Demonstrates how we would ingest data from a real PartSelect API.

In this demo the API client simply reads the local sample files, but the
ingestion flow (API client → SQL / RAG ingestion) is identical to what we
would run against the actual PartSelect endpoints.
"""

from __future__ import annotations

from app.data.api_client import PartSelectAPIClient
from app.db import create_tables, session_scope
from app.rag.rag_ingest import ingest_blogs, ingest_repairs
from scripts.ingest_parts import _link_part_to_model, _upsert_model, _upsert_part


def ingest_parts_from_api(client: PartSelectAPIClient) -> None:
    create_tables()

    with session_scope() as session:
        for record in client.fetch_part_records():
            _upsert_part(session, record)

        for record in client.fetch_crossref_records():
            model, _ = _upsert_model(session, record, record.get("appliance_type", ""))
            _link_part_to_model(session, record.get("partselect_number"), model)

        session.commit()


def ingest_documents_from_api(client: PartSelectAPIClient) -> None:
    blogs = client.fetch_blog_documents()
    repairs = client.fetch_repair_guides()

    if blogs:
        ingest_blogs(blogs)
    if repairs:
        ingest_repairs(repairs)


def main() -> None:
    client = PartSelectAPIClient()
    ingest_parts_from_api(client)
    ingest_documents_from_api(client)
    print("✅ Synced demo data via PartSelectAPIClient (stub).")


if __name__ == "__main__":
    main()

