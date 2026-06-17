def format_learning_objectives(objectives: list[str]) -> str:
    """Format learning objectives for lecturer-facing output."""
    return "\n".join(f"- {objective}" for objective in objectives)


def build_basic_rubric(criteria: list[str], levels: list[str]) -> dict:
    """Create a simple rubric structure."""
    return {
        "criteria": criteria,
        "levels": levels,
    }
