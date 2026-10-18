from pathlib import Path
from alfred_ml.config import AlfredConfig


def test_default_config():
    cfg = AlfredConfig()
    assert cfg.collection_name == "alfred_docs"
    assert cfg.chunk_size == 900
    assert cfg.chunk_overlap == 120
    assert cfg.top_k == 6
    assert isinstance(cfg.docs_dir, Path)
    assert isinstance(cfg.db_dir, Path)


def test_config_save_and_load(tmp_path, monkeypatch):
    custom_cfg_file = tmp_path / "test_alfred_config.json"
    monkeypatch.setattr("alfred_ml.config.CONFIG_FILE", custom_cfg_file)

    cfg = AlfredConfig(
        docs_dir=tmp_path / "custom_docs",
        db_dir=tmp_path / "custom_db",
        top_k=10,
        ollama_model="llama3.2:3b",
    )
    cfg.save()

    assert custom_cfg_file.exists()

    loaded = AlfredConfig.load()
    assert loaded.top_k == 10
    assert loaded.ollama_model == "llama3.2:3b"
    assert loaded.docs_dir == tmp_path / "custom_docs"
    assert loaded.db_dir == tmp_path / "custom_db"
