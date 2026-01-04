from sentence_transformers import SentenceTransformer

from .store import open_store
from .llm import ollama_generate
from .config import AlfredConfig

SYSTEM_STYLE = """You are Alfred ML: concise, correct, and grounded in provided context.
If the context does not contain the answer, say so and suggest what to add.
"""

def build_prompt(question: str, contexts: list[str]) -> str:
    joined = "\n\n---\n\n".join(contexts)
    return f"""{SYSTEM_STYLE}

CONTEXT:
{joined}

USER QUESTION:
{question}

Answer using only the context when possible. If missing, say what is missing.
"""

def ask(cfg: AlfredConfig, question: str) -> dict[str, object]:
    collection = open_store(str(cfg.db_dir), cfg.collection_name)
    embedder = SentenceTransformer(cfg.embed_model)

    q_emb = embedder.encode([question], normalize_embeddings=True).tolist()[0]
    results = collection.query(
        query_embeddings=[q_emb],
        n_results=cfg.top_k,
        include=["documents", "metadatas", "distances"],
    )

    docs = results["documents"][0] if results.get("documents") else []
    metas = results["metadatas"][0] if results.get("metadatas") else []

    prompt = build_prompt(question, docs)
    answer = ollama_generate(cfg.ollama_host, cfg.ollama_model, prompt)

    sources = [{"file_path": m.get("file_path"), "chunk_index": m.get("chunk_index")} for m in metas]
    return {"answer": answer.strip(), "sources": sources}
