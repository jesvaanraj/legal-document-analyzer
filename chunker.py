"""Split long legal documents into smaller chunks (paragraph-aware, with overlap)."""

from typing import List


def chunk_text(text: str, max_chars: int = 6000, overlap: int = 300) -> List[str]:
    """Split `text` into chunks of at most ~max_chars, preferring paragraph boundaries."""
    text = text.strip()
    if len(text) <= max_chars:
        return [text]

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: List[str] = []
    current = ""

    for para in paragraphs:
        # A single huge paragraph: hard-split it.
        while len(para) > max_chars:
            if current:
                chunks.append(current)
                current = ""
            chunks.append(para[:max_chars])
            para = para[max_chars - overlap:]

        if len(current) + len(para) + 2 <= max_chars:
            current = f"{current}\n\n{para}" if current else para
        else:
            chunks.append(current)
            tail = current[-overlap:] if overlap else ""
            current = f"{tail}\n\n{para}" if tail else para

    if current:
        chunks.append(current)
    return chunks
