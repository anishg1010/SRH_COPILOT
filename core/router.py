def route_query(query: str) -> dict:
    """Rule-based router for the first MVP.

    Later this can be replaced by an LLM-based classifier.
    """
    q = query.lower()

    if "rubric" in q or "bewertungsraster" in q:
        intent = "create_rubric"
    elif "learning objective" in q or "lernziel" in q or "learning outcome" in q:
        intent = "generate_learning_objectives"
    elif "assessment" in q or "prüfung" in q:
        intent = "create_assessment"
    elif "teaching method" in q or "aktivität" in q or "activity" in q:
        intent = "suggest_teaching_methods"
    elif "ai" in q or "künstliche intelligenz" in q:
        intent = "suggest_responsible_ai_use"
    else:
        intent = "answer_teaching_question"

    return {
        "agent": "linc",
        "intent": intent,
    }
