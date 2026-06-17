from agents.linc.prompts import LINC_RAG_PROMPT_TEMPLATE, LINC_SYSTEM_PROMPT
from core.llm_client import generate_response
from core.rag_pipeline import RAGPipeline


class LINCAgent:
    """Learning and Innovation Agent.

    Supports lecturers with competence-oriented teaching design.
    """

    def __init__(self) -> None:
        self.collection_name = "linc"
        self.rag = RAGPipeline()

    def answer(self, query: str, language: str = "en", intent: str = "answer_teaching_question") -> str:
        chunks = self.rag.retrieve(
            query=query,
            collection_name=self.collection_name,
            filters={"agent": "linc"},
            top_k=5,
        )

        context = self.rag.build_context(chunks)

        prompt = LINC_RAG_PROMPT_TEMPLATE.format(
            system_prompt=LINC_SYSTEM_PROMPT,
            language=language,
            intent=intent,
            context=context if context else "No internal context retrieved.",
            query=query,
        )

        return generate_response(prompt)
