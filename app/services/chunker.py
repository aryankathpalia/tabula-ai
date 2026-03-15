# app/services/chunker.py

import re
from typing import List


def clean_text_for_chunking(text: str) -> str:
    """
    Normalize whitespace and remove excessive newlines.
    """
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)  # collapse excessive spacing
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()


def chunk_text(
    text: str,
    min_chars: int = 300,
    max_chars: int = 1200,
    overlap: int = 150
) -> List[str]:
    """
    Intelligent legal document chunking:

    - Splits by paragraph
    - Merges small paragraphs
    - Keeps chunk size under max_chars
    - Adds overlap for contextual continuity
    """

    text = clean_text_for_chunking(text)

    paragraphs = text.split("\n\n")

    chunks = []
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()

        if not para:
            continue

        # If paragraph itself is huge, split by sentences
        if len(para) > max_chars:
            sentences = re.split(r'(?<=[.!?])\s+', para)
        else:
            sentences = [para]

        for sentence in sentences:
            if len(current_chunk) + len(sentence) < max_chars:
                current_chunk += " " + sentence
            else:
                if len(current_chunk.strip()) >= min_chars:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence

    # Add last chunk
    if len(current_chunk.strip()) >= min_chars:
        chunks.append(current_chunk.strip())

    # Add overlap for better semantic continuity
    if overlap > 0 and len(chunks) > 1:
        overlapped_chunks = []

        for i in range(len(chunks)):
            chunk = chunks[i]

            if i > 0:
                previous_chunk = chunks[i - 1]
                overlap_text = previous_chunk[-overlap:]
                chunk = overlap_text + " " + chunk

            overlapped_chunks.append(chunk.strip())

        return overlapped_chunks

    return chunks