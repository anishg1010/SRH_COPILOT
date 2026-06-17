from core.language import detect_language
from core.router import route_query
from agents.linc.agent import LINCAgent


def handle_user_query(query: str) -> str:
    """Main orchestration entry point for user queries."""
    language = detect_language(query)
    route = route_query(query)

    if route["agent"] == "linc":
        agent = LINCAgent()
        return agent.answer(query=query, language=language, intent=route["intent"])

    return "No suitable agent found for this query."
