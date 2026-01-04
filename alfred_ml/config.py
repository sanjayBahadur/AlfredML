import json
from dataclasses import dataclass, asdict
from pathlib import Path

CONFIG_FILE = Path("alfred_config.json")

@dataclass
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

    @classmethod
    def load(cls) -> "AlfredConfig":
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
                # Convert path strings back to Path objects
                if "docs_dir" in data: data["docs_dir"] = Path(data["docs_dir"])
                if "db_dir" in data: data["db_dir"] = Path(data["db_dir"])
                return cls(**data)
            except Exception:
                pass
        return cls()

    def save(self):
        data = asdict(self)
        # Convert Path objects to strings
        data["docs_dir"] = str(data["docs_dir"])
        data["db_dir"] = str(data["db_dir"])
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=2)
