import json
import os
from uuid import uuid4

import psycopg
from langchain_core.documents import Document

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres_user:postgres_password@postgres:5432/postgres",
)

from app.rag.embeddings import get_embedding_model

def get_connection():
    return psycopg.connect(DATABASE_URL)

def metadata_to_json(metadata: dict | None) -> str:
    if metadata is None:
        return "{}"

    try:
        return json.dumps(metadata, ensure_ascii=False, default=str)
    except TypeError:
        safe_metadata = {
            key: str(value)
            for key, value in metadata.items()
        }
        return json.dumps(safe_metadata, ensure_ascii=False)
    
def insert_documents_pgvector(documents: list[Document]) -> int:
    inserted_count = 0

    embedding_model = get_embedding_model()

    with get_connection() as conn:
        with conn.cursor() as cur:
            for doc in documents:
                chunk_id = str(uuid4())
                embedding = embedding_model.embed_query(doc.page_content)
                metadata_json = metadata_to_json(doc.metadata)
                file_name = doc.metadata.get("file_name", "")
                file_type = doc.metadata.get("file_type", "")
                source_file = doc.metadata.get("source_file", "")

                cur.execute(
                    """
                    INSERT INTO rag_document_chunks (chunk_id, source_file, file_name, file_type, content, metadata, embedding)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (chunk_id, source_file, file_name, file_type, doc.page_content, metadata_json, embedding),
                )
                inserted_count += 1

            conn.commit()

    return inserted_count

def search_documents_pgvector(query: str, k: int = 4) -> list[dict]:
    embedding_model = get_embedding_model()
    query_embedding = embedding_model.embed_query(query)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 
                    chunk_id, 
                    source_file, 
                    file_name, 
                    file_type, 
                    content, 
                    metadata,
                    embedding <=> %s::vector AS distance 
                FROM rag_document_chunks
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (query_embedding, 
                 query_embedding, 
                 k,
                ),
            )
            results = cur.fetchall()
    result = []

    for row in results:
        result.append(
            {
            "chunk_id": row[0],
            "source_file": row[1],
            "file_name": row[2],
            "file_type": row[3],
            "content": row[4],
            "metadata": row[5],
            "distance": row[6],
        }
    )

    return result

def format_search_results_pgvector(results: list[dict]) -> str:
    formatted = []
    for idx, result in enumerate(results, start=1):
        content = result.get("content", "")
        metadata = result.get("metadata", {})
        source = metadata.get("source_file", "Unknown source")
        file_name = metadata.get("file_name", "Unknown file name")
        file_type = metadata.get("file_type", "Unknown file type")
        distance = result.get("distance", "Unknown distance")

        formatted.append(
            f"Source: {source}\n"
            f"Result {idx}:\n"
            f"Content: {content}\n"
            f"Distance: {distance}"
        )

    return "\n\n---\n\n".join(formatted)