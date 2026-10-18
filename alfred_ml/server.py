from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .config import AlfredConfig
from .ingest import ingest_all
from .llm import check_connection, list_models
from .rag import ask

app = FastAPI(
    title="Alfred ML API",
    description="Local, privacy-focused RAG assistant REST API",
    version="1.1.0",
)


class AskRequest(BaseModel):
    question: str = Field(..., description="The user query or question")
    top_k: Optional[int] = Field(None, ge=1, le=20, description="Number of context chunks to retrieve")
    model: Optional[str] = Field(None, description="Ollama model override")


class SourceItem(BaseModel):
    file_path: Optional[str] = None
    chunk_index: Optional[int] = None


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceItem]


class IngestResponse(BaseModel):
    added_chunks: int
    skipped_files: int
    deleted_files: int


@app.get("/health")
def health() -> dict[str, Any]:
    cfg = AlfredConfig.load()
    ollama_ok = check_connection(cfg.ollama_host)
    return {
        "status": "healthy",
        "ollama_connected": ollama_ok,
        "ollama_host": cfg.ollama_host,
        "active_model": cfg.ollama_model,
    }


@app.get("/models")
def get_models() -> dict[str, Any]:
    cfg = AlfredConfig.load()
    models = list_models(cfg.ollama_host)
    return {"active_model": cfg.ollama_model, "available_models": models}


@app.get("/config")
def get_config() -> dict[str, Any]:
    cfg = AlfredConfig.load()
    return {
        "docs_dir": str(cfg.docs_dir),
        "db_dir": str(cfg.db_dir),
        "collection_name": cfg.collection_name,
        "embed_model": cfg.embed_model,
        "ollama_host": cfg.ollama_host,
        "ollama_model": cfg.ollama_model,
        "chunk_size": cfg.chunk_size,
        "chunk_overlap": cfg.chunk_overlap,
        "top_k": cfg.top_k,
    }


@app.post("/ask", response_model=AskResponse)
def ask_question(req: AskRequest) -> AskResponse:
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    cfg = AlfredConfig.load()
    if req.top_k:
        cfg.top_k = req.top_k
    if req.model:
        cfg.ollama_model = req.model

    try:
        out = ask(cfg, req.question)
        return AskResponse(
            answer=out["answer"],
            sources=[
                SourceItem(
                    file_path=s.get("file_path"),
                    chunk_index=s.get("chunk_index"),
                )
                for s in out.get("sources", [])
            ],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest", response_model=IngestResponse)
def trigger_ingest() -> IngestResponse:
    cfg = AlfredConfig.load()
    try:
        stats = ingest_all(cfg)
        return IngestResponse(
            added_chunks=stats.get("added_chunks", 0),
            skipped_files=stats.get("skipped_files", 0),
            deleted_files=stats.get("deleted_files", 0),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
