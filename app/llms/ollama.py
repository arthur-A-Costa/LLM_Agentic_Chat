import os

from langchain_ollama import ChatOllama


OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")

DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:8b")
ROUTER_MODEL = os.getenv("ROUTER_MODEL", DEFAULT_MODEL)
SALESMAN_MODEL = os.getenv("SALESMAN_MODEL", DEFAULT_MODEL)
CONSULTANT_MODEL = os.getenv("CONSULTANT_MODEL", DEFAULT_MODEL)
REVIEWER_MODEL = os.getenv("REVIEWER_MODEL", DEFAULT_MODEL)


def get_router_llm():
    return ChatOllama(
        model=ROUTER_MODEL,
        base_url=OLLAMA_BASE_URL,
        validate_model_on_init=True,
        temperature=0,
    )


def get_salesman_llm():
    return ChatOllama(
        model=SALESMAN_MODEL,
        base_url=OLLAMA_BASE_URL,
        validate_model_on_init=True,
        temperature=0.2,
    )


def get_consultant_llm():
    return ChatOllama(
        model=CONSULTANT_MODEL,
        base_url=OLLAMA_BASE_URL,
        validate_model_on_init=True,
        temperature=0.1,
    )


def get_reviewer_llm():
    return ChatOllama(
        model=REVIEWER_MODEL,
        base_url=OLLAMA_BASE_URL,
        validate_model_on_init=True,
        temperature=0,
    )