import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


def load_jsonl(path: str | Path) -> list[dict]:
    path = Path(path)
    records = []

    if not path.exists():
        return records

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                records.append(json.loads(line))

    return records


def embed_and_store_chunks(
    chunks_path: str | Path = "data/processed/linc/chunks.jsonl",
    collection_name: str = "linc",
    db_path: str = "data/vector_db/chroma",
    embedding_model_name: str = "intfloat/multilingual-e5-small",
) -> None:
    """Embed chunks and store them in ChromaDB."""
    chunks = load_jsonl(chunks_path)
    if not chunks:
        print("No chunks found to embed.")
        return

    model = SentenceTransformer(embedding_model_name)
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_or_create_collection(name=collection_name)

    ids = [chunk["chunk_id"] for chunk in chunks]
    documents = [chunk["text"] for chunk in chunks]
    metadatas = [
        {key: value for key, value in chunk.items() if key != "text"}
        for chunk in chunks
    ]
    embeddings = model.encode(documents, normalize_embeddings=True).tolist()

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    print(f"Stored {len(chunks)} chunks in Chroma collection '{collection_name}'.")
