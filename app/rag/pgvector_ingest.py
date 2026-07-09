from pathlib import Path
import os
from uuid import uuid4

import psycopg
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.rag.embeddings import get_embedding_model
from app.rag.loader import load_documents
from app.rag.pgvector_store import insert_documents_pgvector

RAG_SOURCE_DIR = os.getenv("RAG_SOURCE_DIR", "app/data/rag_resources")

def document_splitter(documents):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
    )

    return splitter.split_documents(documents)

def ingest_documents(reset: bool = False):
    """
    Ingest documents into the PGVector PostgreSQL database.

    If reset is True, the existing collection will be deleted and recreated.
    """
    # Load documents from the source directory
    documents = load_documents(RAG_SOURCE_DIR)

    if not documents:
        print(f"No documents to ingest.")
        return

    # Split documents into chunks
    document_chunks = document_splitter(documents)
    embedding_model = get_embedding_model()

    if reset:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("TRUNCATE TABLE rag_document_chunks_bge_m3;")
            conn.commit()

    inserted_count = insert_documents_pgvector(document_chunks)

if __name__ == "__main__":
    ingest_documents(reset=False)
