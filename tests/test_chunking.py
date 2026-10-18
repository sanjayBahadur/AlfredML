from alfred_ml.chunking import chunk_text


def test_chunk_text_basic():
    text = "The quick brown fox jumps over the lazy dog."
    chunks = chunk_text(text, chunk_size=20, overlap=5)
    assert len(chunks) >= 2
    assert chunks[0] == "The quick brown fox"
    # Ensure all chunks are non-empty
    assert all(len(c) > 0 for c in chunks)


def test_chunk_text_empty():
    assert chunk_text("", chunk_size=100, overlap=20) == []
    assert chunk_text("   \n\t   ", chunk_size=100, overlap=20) == []


def test_chunk_text_overlap_greater_or_equal_to_size():
    # Crucial test: ensure no infinite loop when overlap >= chunk_size
    text = "Hello world this is a test string for edge cases."
    chunks = chunk_text(text, chunk_size=10, overlap=15)
    assert len(chunks) > 0
    # Step should be 1 char, ensuring forward progress
    assert all(len(c) <= 10 for c in chunks)


def test_chunk_text_zero_overlap():
    text = "1234567890abcdefghij"
    chunks = chunk_text(text, chunk_size=10, overlap=0)
    assert len(chunks) == 2
    assert chunks[0] == "1234567890"
    assert chunks[1] == "abcdefghij"


def test_chunk_text_invalid_chunk_size():
    assert chunk_text("some text", chunk_size=0, overlap=0) == []
    assert chunk_text("some text", chunk_size=-5, overlap=0) == []
