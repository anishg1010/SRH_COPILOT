from core.language import detect_language


def detect_document_language(text: str) -> str:
    """Detect whether a document chunk is English, German, mixed, or unknown."""
    detected = detect_language(text)

    if detected in {"en", "de"}:
        return detected

    return "unknown"
