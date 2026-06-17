import json
from pathlib import Path

from ingestion.extract_text import extract_pdf_text
from ingestion.detect_language import detect_document_language
from ingestion.classify_document import classify_linc_document
from ingestion.create_metadata import create_document_metadata
from ingestion.clean_text import clean_text
from ingestion.chunk_documents import create_chunks


RAW_INBOX = Path("data/raw/linc/inbox")
DOCUMENTS_OUT = Path("data/processed/linc/documents.jsonl")
CHUNKS_OUT = Path("data/processed/linc/chunks.jsonl")


def append_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")


def ingest_linc_pdfs() -> None:
    """Run the basic LINC ingestion pipeline for PDFs in the inbox."""
    pdf_files = list(RAW_INBOX.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in {RAW_INBOX}")
        return

    for pdf in pdf_files:
        print(f"Processing: {pdf.name}")

        pages = extract_pdf_text(pdf)
        cleaned_pages = [
            {
                "page": item["page"],
                "text": clean_text(item["text"]),
            }
            for item in pages
        ]

        full_text = "\n\n".join(page["text"] for page in cleaned_pages)
        language = detect_document_language(full_text)
        classification = classify_linc_document(full_text, pdf.name)

        document_metadata = create_document_metadata(
            file_path=pdf,
            agent=classification["agent"],
            department=classification["department"],
            category=classification["category"],
            language=language,
            document_type="pdf",
            status="draft",
        )

        document_record = {
            **document_metadata,
            "text": full_text,
        }

        chunks = create_chunks(cleaned_pages, document_metadata)

        append_jsonl(DOCUMENTS_OUT, [document_record])
        append_jsonl(CHUNKS_OUT, chunks)

        print(f"Created {len(chunks)} chunks for {pdf.name}")

    print("Ingestion complete.")


if __name__ == "__main__":
    ingest_linc_pdfs()
