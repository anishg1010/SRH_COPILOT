from pathlib import Path
import re
import uuid


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


def create_document_metadata(
    file_path: str | Path,
    agent: str,
    department: str,
    category: str,
    language: str,
    document_type: str = "document",
    access_level: str = "lecturer",
    status: str = "draft",
) -> dict:
    """Create document-level metadata."""
    file_path = Path(file_path)
    stem = slugify(file_path.stem)
    document_id = f"{agent}_{category}_{stem}_{uuid.uuid4().hex[:8]}"

    return {
        "document_id": document_id,
        "agent": agent,
        "department": department,
        "category": category,
        "document_type": document_type,
        "language": language,
        "source_file": file_path.name,
        "access_level": access_level,
        "status": status,
    }
