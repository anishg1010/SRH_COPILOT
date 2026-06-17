def build_source_summary(chunks: list[dict]) -> str:
    """Create a small source summary for UI/debug output."""
    if not chunks:
        return "No internal sources retrieved."

    lines = []
    for idx, chunk in enumerate(chunks, start=1):
        meta = chunk.get("metadata", {})
        lines.append(
            f"{idx}. {meta.get('source_file', 'unknown')} "
            f"(page {meta.get('page', 'unknown')}, topic {meta.get('topic', 'general')})"
        )
    return "\n".join(lines)
