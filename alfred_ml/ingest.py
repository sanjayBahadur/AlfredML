import hashlib
from pathlib import Path
from typing import Iterable

from sentence_transformers import SentenceTransformer

from .chunking import chunk_text
from .store import open_store
from .config import AlfredConfig

TEXT_EXTS = {".txt", ".md"}

def file_sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()

def iter_docs(docs_dir: Path) -> Iterable[Path]:
    for p in docs_dir.rglob("*"):
        if p.is_file() and p.suffix.lower() in TEXT_EXTS:
            yield p

def ingest_all(cfg: AlfredConfig) -> dict[str, int]:
    cfg.docs_dir.mkdir(parents=True, exist_ok=True)
    cfg.db_dir.mkdir(parents=True, exist_ok=True)

    collection = open_store(str(cfg.db_dir), cfg.collection_name)
    embedder = SentenceTransformer(cfg.embed_model)

    added_chunks = 0
    skipped_files = 0

    existing_in_db = set()
    
    # 1. Get all files currently in the DB
    try:
        # We fetch all metadatas to know what paths exist
        # This might be slow for huge datasets, but okay for personal docs
        all_data = collection.get(include=["metadatas"])
        if all_data and all_data.get("metadatas"):
            for m in all_data["metadatas"]:
                if m and "file_id" in m:
                    existing_in_db.add(m["file_id"])
    except Exception:
        pass # DB might be empty

    current_file_ids = set()

    # 2. Ingest new/modified files
    for path in iter_docs(cfg.docs_dir):
        sha = file_sha256(path)
        file_id = f"{path.as_posix()}::{sha}"
        current_file_ids.add(file_id)

        existing = collection.get(where={"file_id": file_id}, limit=1)
        if existing and existing.get("ids"):
            skipped_files += 1
            continue

        text = path.read_text(encoding="utf-8", errors="ignore")
        chunks = chunk_text(text, cfg.chunk_size, cfg.chunk_overlap)
        if not chunks:
            skipped_files += 1
            continue

        embeddings = embedder.encode(chunks, normalize_embeddings=True).tolist()

        ids = [f"{file_id}::chunk::{i}" for i in range(len(chunks))]
        metadatas = [{
            "file_path": path.as_posix(),
            "file_sha256": sha,
            "file_id": file_id,
            "chunk_index": i,
        } for i in range(len(chunks))]

        collection.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        added_chunks += len(chunks)

    # 3. Remove deleted files
    # Any file_id in DB that is NOT in current_file_ids means either:
    # - The file was deleted
    # - The file changed (SHA changed), so the OLD file_id should be removed
    to_delete = existing_in_db - current_file_ids
    if to_delete:
        collection.delete(where={"file_id": {"$in": list(to_delete)}})

    return {"added_chunks": added_chunks, "skipped_files": skipped_files, "deleted_files": len(to_delete)}
