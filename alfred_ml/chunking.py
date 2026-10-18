def chunk_text(text: str, chunk_size: int = 900, overlap: int = 120) -> list[str]:
    """
    Split text into overlapping chunks of characters.

    Ensures forward progress even if overlap >= chunk_size.
    """
    text = text.strip()
    if not text or chunk_size <= 0:
        return []

    # Ensure overlap is strictly less than chunk_size to guarantee forward progress
    safe_overlap = max(0, min(overlap, chunk_size - 1))
    step = chunk_size - safe_overlap

    chunks: list[str] = []
    start = 0
    n = len(text)

    while start < n:
        end = min(start + chunk_size, n)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= n:
            break
        start += step

    return chunks
