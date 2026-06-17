from typing import Iterator


def chunk_words(text: str, chunk_size: int = 500, overlap: int = 75) -> Iterator[str]:
    """Simple word-based chunker for the MVP."""
    words = text.split()
    if not words:
        return

    start = 0
    while start < len(words):
        end = start + chunk_size
        yield " ".join(words[start:end])
        if end >= len(words):
            break
        start = max(0, end - overlap)


def create_chunks(page_records: list[dict], document_metadata: dict) -> list[dict]:
    """Create chunk records with chunk-level metadata."""
    chunks = []
    counter = 1

    for page in page_records:
        page_number = page["page"]
        text = page["text"]

        for chunk_text in chunk_words(text):
            chunk_id = f"{document_metadata['document_id']}_chunk_{counter:04d}"

            chunks.append(
                {
                    "chunk_id": chunk_id,
                    "document_id": document_metadata["document_id"],
                    "agent": document_metadata["agent"],
                    "department": document_metadata["department"],
                    "category": document_metadata["category"],
                    "topic": "general",
                    "language": document_metadata["language"],
                    "page": page_number,
                    "source_file": document_metadata["source_file"],
                    "text": chunk_text,
                }
            )

            counter += 1

    return chunks
