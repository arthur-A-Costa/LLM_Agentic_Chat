# bge-m3 OR nomic-embed-text (curent)
import os

from langchain_ollama import OllamaEmbeddings


OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
# EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "bge-m3")


def get_embedding_model() -> OllamaEmbeddings:
    """
    Return the embedding model used to convert text chunks into vectors.

    This uses Ollama, so the model must exist inside the Ollama container:
    docker compose exec ollama ollama pull nomic-embed-text
    """

    return OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=OLLAMA_BASE_URL,
    )