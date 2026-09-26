#!/usr/bin/env python3

import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm


CHUNKS_FILE = Path("data/chunks.jsonl")
INDEX_DIR = Path("index")

INDEX_DIR.mkdir(exist_ok=True)

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def load_chunks():

    chunks = []

    with CHUNKS_FILE.open(
        encoding="utf-8"
    ) as f:

        for line in f:
            if line.strip():
                chunks.append(json.loads(line))

    return chunks


def main():

    chunks = load_chunks()

    print(f"Chunks: {len(chunks)}")

    print(
        f"Loading embedding model: {MODEL_NAME}"
    )

    model = SentenceTransformer(MODEL_NAME)

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    embeddings = embeddings.astype(
        "float32"
    )

    dimension = embeddings.shape[1]

    # Exact cosine-similarity search.
    index = faiss.IndexFlatIP(dimension)

    index.add(embeddings)

    faiss.write_index(
        index,
        str(INDEX_DIR / "faiss.index"),
    )

    np.save(
        INDEX_DIR / "embeddings.npy",
        embeddings,
    )

    with (
        INDEX_DIR / "metadata.json"
    ).open("w", encoding="utf-8") as f:

        json.dump(
            {
                "model": MODEL_NAME,
                "dimension": dimension,
                "chunks": len(chunks),
            },
            f,
            indent=2,
        )

    print()
    print("FAISS index created.")
    print(f"Vectors: {index.ntotal}")
    print(f"Dimensions: {dimension}")


if __name__ == "__main__":
    main()
