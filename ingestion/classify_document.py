def classify_linc_document(text: str, file_name: str = "") -> dict:
    """Rule-based LINC document classifier for the MVP.

    Later this can be replaced by an Ollama-based classifier with human review.
    """
    lower_text = f"{file_name} {text}".lower()

    if "rubric" in lower_text or "assessment" in lower_text or "prüfung" in lower_text:
        category = "assessment_rubrics"
    elif "learning objective" in lower_text or "learning outcome" in lower_text or "lernziel" in lower_text:
        category = "core_principles"
    elif "module" in lower_text or "course design" in lower_text or "curriculum" in lower_text:
        category = "module_design"
    elif "teaching method" in lower_text or "didactic" in lower_text or "lehrmethode" in lower_text:
        category = "teaching_methods"
    elif "artificial intelligence" in lower_text or "responsible ai" in lower_text or "künstliche intelligenz" in lower_text:
        category = "responsible_ai"
    elif "policy" in lower_text or "guideline" in lower_text or "ordnung" in lower_text:
        category = "policies"
    else:
        category = "general"

    return {
        "agent": "linc",
        "department": "learning_and_innovation",
        "category": category,
    }
