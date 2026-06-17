from pathlib import Path
import fitz


def extract_pdf_text(file_path: str | Path) -> list[dict]:
    """Extract text from a PDF as page-level records."""
    file_path = Path(file_path)
    pages = []

    with fitz.open(file_path) as doc:
        for page_index, page in enumerate(doc, start=1):
            pages.append(
                {
                    "page": page_index,
                    "text": page.get_text("text"),
                }
            )

    return pages
