from pathlib import Path
from alfred_ml.ingest import extract_text_from_file, file_sha256, SUPPORTED_EXTS


def test_supported_extensions():
    assert ".txt" in SUPPORTED_EXTS
    assert ".md" in SUPPORTED_EXTS
    assert ".pdf" in SUPPORTED_EXTS
    assert ".py" in SUPPORTED_EXTS
    assert ".ts" in SUPPORTED_EXTS


def test_extract_text_plain(tmp_path):
    f = tmp_path / "sample.py"
    f.write_text("def hello():\n    return 'world'\n", encoding="utf-8")
    extracted = extract_text_from_file(f)
    assert "def hello():" in extracted
    assert "return 'world'" in extracted


def test_file_sha256(tmp_path):
    f = tmp_path / "doc.txt"
    f.write_text("test content", encoding="utf-8")
    sha1 = file_sha256(f)
    assert len(sha1) == 64
    f.write_text("different content", encoding="utf-8")
    sha2 = file_sha256(f)
    assert sha1 != sha2
