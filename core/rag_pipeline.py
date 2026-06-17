from pathlib import Path
from typing import Any

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer


class RAGPipeline:
    """Shared RAG pipeline used by all agents."""

    def __init__(
        self,
        db_path: str = "data/vector_db/chroma",
        embedding_model: str = "intfloat/multilingual-e5-small",
    ) -> None:
        self.client = chromadb.PersistentClient(
        path=db_path,
        settings=Settings(anonymized_telemetry=False)
     )
        self.embedding_model = SentenceTransformer(embedding_model)

    def get_collection(self, collection_name: str):
        return self.client.get_or_create_collection(name=collection_name)

    def retrieve(
        self,
        query: str,
        collection_name: str,
        filters: dict[str, Any] | None = None,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Retrieve relevant chunks from ChromaDB."""
        collection = self.get_collection(collection_name)
        query_embedding = self.embedding_model.encode(query, normalize_embeddings=True).tolist()

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filters,
            include=["documents", "metadatas", "distances"],
        )

        chunks = []
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for text, metadata, distance in zip(documents, metadatas, distances):
            chunks.append(
                {
                    "text": text,
                    "metadata": metadata,
                    "distance": distance,
                }
            )

        return chunks

    @staticmethod
    def build_context(chunks: list[dict[str, Any]]) -> str:
        """Convert retrieved chunks into a prompt-ready context block."""
        parts = []
        for index, chunk in enumerate(chunks, start=1):
            metadata = chunk.get("metadata", {})
            source = metadata.get("source_file", "unknown source")
            page = metadata.get("page", "unknown page")
            parts.append(
                f"[Source {index}: {source}, page {page}]\n{chunk['text']}"
            )
        return "\n\n".join(parts)
