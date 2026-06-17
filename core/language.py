from langdetect import detect, LangDetectException


def detect_language(text: str) -> str:
    """Detect language and normalize to simple labels."""
    try:
        code = detect(text)
    except LangDetectException:
        return "unknown"

    if code.startswith("de"):
        return "de"
    if code.startswith("en"):
        return "en"
    return code
