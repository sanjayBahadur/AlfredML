import hashlib
import logging
from pathlib import Path
from typing import Iterable

from sentence_transformers import SentenceTransformer

from .chunking import chunk_text
from .config import AlfredConfig
from .store import open_store

logger = logging.getLogger(__name__)

SUPPORTED_EXTS = {
    # Documents
    ".txt",
    ".md",
    ".markdown",
    ".pdf",
    # Code & Configs
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".sh",
    ".bash",
    ".sql",
    ".html",
    ".css",
    ".c",
    ".cpp",
    ".h",
    ".rs",
    ".go",
}


def file_sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def extract_text_from_file(p: Path) -> str:
    suffix = p.suffix.lower()
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader

            reader = PdfReader(str(p))
            pages: list[str] = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
            return "\n\n".join(pages)
        except Exception as e:
            logger.warning("Failed to extract PDF %s: %s", p, e)
            return ""
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        logger.warning("Failed to read text from %s: %s", p, e)
        return ""


def iter_docs(docs_dir: Path) -> Iterable[Path]:
    if not docs_dir.exists():
        return
    for p in docs_dir.rglob("*"):
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS:
            yield p


def ingest_all(cfg: AlfredConfig) -> dict[str, int]:
    cfg.docs_dir.mkdir(parents=True, exist_ok=True)
    cfg.db_dir.mkdir(parents=True, exist_ok=True)

    collection = open_store(str(cfg.db_dir), cfg.collection_name)
    embedder = SentenceTransformer(cfg.embed_model)

    added_chunks = 0
    skipped_files = 0
    deleted_files = 0

    existing_in_db: set[str] = set()

    # 1. Get all files currently in the DB
    try:
        all_data = collection.get(include=["metadatas"])
        if all_data and all_data.get("metadatas"):
            for m in all_data["metadatas"]:
                if m and "file_id" in m:
                    existing_in_db.add(m["file_id"])
    except Exception:
        pass  # DB might be empty

    current_file_ids: set[str] = set()

    # 2. Ingest new/modified files
    for path in iter_docs(cfg.docs_dir):
        try:
            sha = file_sha256(path)
        except Exception:
            skipped_files += 1
            continue

        file_id = f"{path.as_posix()}::{sha}"
        current_file_ids.add(file_id)

        try:
            existing = collection.get(where={"file_id": file_id}, limit=1)
            if existing and existing.get("ids"):
                skipped_files += 1
                continue
        except Exception:
            pass

        text = extract_text_from_file(path)
        chunks = chunk_text(text, cfg.chunk_size, cfg.chunk_overlap)
        if not chunks:
            skipped_files += 1
            continue

        embeddings = embedder.encode(chunks, normalize_embeddings=True).tolist()

        ids = [f"{file_id}::chunk::{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "file_path": path.as_posix(),
                "file_sha256": sha,
                "file_id": file_id,
                "chunk_index": i,
            }
            for i in range(len(chunks))
        ]

        collection.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        added_chunks += len(chunks)

    # 3. Remove deleted/outdated files
    to_delete = existing_in_db - current_file_ids
    if to_delete:
        delete_list = list(to_delete)
        for i in range(0, len(delete_list), 100):
            batch = delete_list[i : i + 100]
            try:
                collection.delete(where={"file_id": {"$in": batch}})
                deleted_files += len(batch)
            except Exception as e:
                logger.warning("Failed to delete outdated vectors: %s", e)

    return {
        "added_chunks": added_chunks,
        "skipped_files": skipped_files,
        "deleted_files": deleted_files,
    }
