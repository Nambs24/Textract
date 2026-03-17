from typing import List


def chunk_text(
    text: str,
    chunk_size: int = 800,
    overlap: int = 120,
) -> List[str]:
    """
    Splits large text into overlapping chunks.

    Optimized for:
    - RAG retrieval quality
    - Gemini embedding context window
    """

    if not text:
        return []

    text = clean_text(text)

    chunks = []
    start = 0
    length = len(text)

    while start < length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap

    return chunks


def clean_text(text: str) -> str:
    """
    Basic normalization for better embedding quality.
    """
    return " ".join(text.split())
