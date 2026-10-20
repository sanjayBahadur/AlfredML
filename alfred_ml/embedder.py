from functools import lru_cache

from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=4)
def get_embedder(model_name: str) -> SentenceTransformer:
    """Return the embedding model for `model_name`, loading it the first time only.

    Loading the model takes most of a second, so doing it on every question made each
    answer wait before retrieval even started. One loaded model is reused by the CLI, the
    TUI, the API server and the file watcher for as long as the process runs.
    """
    return SentenceTransformer(model_name)
