from pathlib import Path
import os
from uuid import uuid4

from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.rag.embeddings import get_embedding_model
from app.rag.loader import load_documents

CHROMA_HOST = os.getenv("CHROMA_HOST", "chromadb")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "consortium_docs")
RAG_SOURCE_DIR = os.getenv("RAG_SOURCE_DIR", "app/data/rag_resources")

def simplify_document_metadata(documents: list[Document]) -> tuple[list[Document], list[str]]:
    cleaned_documents = []
    ids = []

    for doc in documents:
        chunk_id = str(uuid4())
        ids.append(chunk_id)

        metadata = doc.metadata or {}

        source = metadata.get("source", "")
        file_name = metadata.get("file_name", "")
        file_type = metadata.get("file_type", "")

        # Some Docling metadata may contain an "origin" dict.
        origin = metadata.get("origin", {})
        if isinstance(origin, dict):
            file_name = file_name or origin.get("filename", "")

        cleaned_documents.append(
            Document(
                page_content=doc.page_content,
                metadata={
                    "chunk_id": chunk_id,
                    "source": str(source),
                    "file_name": str(file_name),
                    "file_type": str(file_type),
                },
            )
        )

    return cleaned_documents, ids

def get_chroma_connection() -> Chroma:
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embedding_model(),
        host=CHROMA_HOST,
        port=CHROMA_PORT,
        ssl=False,
    )

def document_splitter(documents):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
    )

    return splitter.split_documents(documents)

def ingest_documents(reset: bool = False):
    """
    Ingest documents into the Chroma database.

    If reset is True, the existing collection will be deleted and recreated.
    """
    # Load documents from the source directory
    documents = load_documents(RAG_SOURCE_DIR)

    if not documents:
        print(f"No documents to ingest.")
        return

    # Split documents into chunks
    document_chunks = document_splitter(documents)
    document_chunks, ids = simplify_document_metadata(document_chunks)
    embedding_model = get_embedding_model()

    # Connect to Chroma
    chroma_db = get_chroma_connection()

    if reset:
        # Delete the existing collection
        chroma_db.delete_collection()
        # Create a new collection
        chroma_db = get_chroma_connection()

    chroma_db.add_documents(
        documents=document_chunks,
        ids=ids,
    )

if __name__ == "__main__":
    ingest_documents(reset=False)

