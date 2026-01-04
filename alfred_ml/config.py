from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class AlfredConfig:
    docs_dir: Path = Path("alfred_docs")
    db_dir: Path = Path("alfred_db")
    collection_name: str = "alfred_docs"
    embed_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:1b-instruct-q4_K_M"
    chunk_size: int = 900
    chunk_overlap: int = 120
    top_k: int = 6
