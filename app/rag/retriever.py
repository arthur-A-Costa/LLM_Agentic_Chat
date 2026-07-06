import os

from langchain_chroma import Chroma

from app.rag.embeddings import get_embedding_model

CHROMA_HOST = os.getenv("CHROMA_HOST", "chromadb")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "consortium_docs")

def get_chroma_connection() -> Chroma:
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embedding_model(),
        host=CHROMA_HOST,
        port=CHROMA_PORT,
        ssl=False,
    )

def search_documents(query: str, k: int = 4) -> list[dict]:
    chroma_db = get_chroma_connection()

    docs = chroma_db.similarity_search(query, k=k)

    return [
        {
            "content": doc.page_content,
            "metadata": doc.metadata,
        }
        for doc in docs
    ]

def format_search_results(results: list[dict]) -> str:
    formatted = []
    for idx, result in enumerate(results, start=1):
        content = result.get("content", "")
        metadata = result.get("metadata", {})
        source = metadata.get("source", "Unknown source")
        file_name = metadata.get("file_name", "Unknown file name")
        file_type = metadata.get("file_type", "Unknown file type")

        formatted.append(
            f"Source: {source}\n"
            f"Result {idx}:\n"
            f"Content:\n{content}"
        )

    return "\n\n---\n\n".join(formatted)