from pathlib import Path

import alfred_ml.embedder as embedder_module
import alfred_ml.rag as rag
from alfred_ml.config import AlfredConfig


class FakeModel:
    loaded: list[str] = []

    def __init__(self, name: str):
        FakeModel.loaded.append(name)

    def encode(self, texts, normalize_embeddings=True):
        import numpy as np

        return np.zeros((len(texts), 3))


class FakeCollection:
    def query(self, **_kwargs):
        return {"documents": [["context"]], "metadatas": [[{"file_path": "a.md", "chunk_index": 0}]]}


def fresh_cache(monkeypatch):
    FakeModel.loaded = []
    monkeypatch.setattr(embedder_module, "SentenceTransformer", FakeModel)
    embedder_module.get_embedder.cache_clear()


def test_the_same_model_is_loaded_once(monkeypatch):
    fresh_cache(monkeypatch)
    first = embedder_module.get_embedder("model-a")
    assert embedder_module.get_embedder("model-a") is first
    assert FakeModel.loaded == ["model-a"]


def test_a_different_model_name_loads_a_different_model(monkeypatch):
    fresh_cache(monkeypatch)
    a = embedder_module.get_embedder("model-a")
    b = embedder_module.get_embedder("model-b")
    assert a is not b
    assert FakeModel.loaded == ["model-a", "model-b"]


def test_asking_several_questions_loads_the_model_once(monkeypatch, tmp_path):
    fresh_cache(monkeypatch)
    monkeypatch.setattr(rag, "open_store", lambda *_a, **_k: FakeCollection())
    monkeypatch.setattr(rag, "ollama_generate", lambda *_a, **_k: "an answer")
    cfg = AlfredConfig(docs_dir=Path(tmp_path / "docs"), db_dir=Path(tmp_path / "db"), embed_model="model-a")
    for question in ("one?", "two?", "three?"):
        assert rag.ask(cfg, question)["answer"] == "an answer"
    assert FakeModel.loaded == ["model-a"]
