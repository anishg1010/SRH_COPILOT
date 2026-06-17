from core.rag_pipeline import RAGPipeline


def test_linc_retrieval_smoke():
    rag = RAGPipeline()
    chunks = rag.retrieve("learning objectives", collection_name="linc", filters={"agent": "linc"}, top_k=3)
    assert isinstance(chunks, list)
