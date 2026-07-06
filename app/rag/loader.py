from pathlib import Path

from langchain_core.documents import Document
from langchain_docling import DoclingLoader

SUPPORTED_EXTENSIONS= {".pdf", ".docx", ".txt", ".md", ".html", ".htm"}

def get_source_files(source_dir: str = "app/data/rag_resources") -> list[Path]:
    
    root = Path(source_dir)

    if not root.exists():
        raise FileNotFoundError(f"Source directory '{source_dir}' does not exist.")
    
    return[
        path 
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    ]

def load_documents(source_dir: str = "app/data/rag_resources") -> list[Document]:
    source_files = get_source_files(source_dir)
    documents: list[Document] = []

    if not source_files:
        raise FileNotFoundError(f"No supported files found in '{source_dir}'. Supported extensions: {SUPPORTED_EXTENSIONS}")
        return []

    for path in source_files:
        # ExportType.DOC_CHUNKS (deafult)
        loader = DoclingLoader(file_path=str(path))
        loaded_docs = loader.load()

        for doc in loaded_docs:
            doc.metadata["source"] = str(path)
            doc.metadata["file_name"] = path.name
            doc.metadata["file_extension"] = path.suffix.lower()

        documents.extend(loaded_docs)
    
    return documents