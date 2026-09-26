#!/usr/bin/env python3

import json
import pickle
from pathlib import Path

import faiss
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer


INDEX_DIR = Path("index")
CHUNKS_FILE = Path("data/chunks.jsonl")

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class HybridRetriever:

    def __init__(
        self,
        dense_weight=0.65,
        lexical_weight=0.35,
    ):

        self.dense_weight = dense_weight
        self.lexical_weight = lexical_weight

        self.model = SentenceTransformer(
            MODEL_NAME
        )

        self.index = faiss.read_index(
            str(INDEX_DIR / "faiss.index")
        )

        self.chunks = []

        with CHUNKS_FILE.open(
            encoding="utf-8"
        ) as f:

            for line in f:
                if line.strip():
                    self.chunks.append(
                        json.loads(line)
                    )

        # BM25 corpus.
        tokenized = [
            self.tokenize(chunk["text"])
            for chunk in self.chunks
        ]

        self.bm25 = BM25Okapi(tokenized)

    @staticmethod
    def tokenize(text):

        return text.lower().split()

    @staticmethod
    def normalize_scores(scores):

        scores = np.asarray(
            scores,
            dtype=np.float32,
        )

        if len(scores) == 0:
            return scores

        min_score = scores.min()
        max_score = scores.max()

        if max_score - min_score < 1e-8:
            return np.ones_like(scores)

        return (
            (scores - min_score)
            / (max_score - min_score)
        )

    def search(
        self,
        query,
        k=5,
        candidate_k=20,
    ):

        # ---------------------------------------------------------
        # Dense retrieval
        # ---------------------------------------------------------

        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True,
        ).astype("float32")

        dense_scores, dense_indices = (
            self.index.search(
                query_embedding,
                candidate_k,
            )
        )

        dense_scores = dense_scores[0]
        dense_indices = dense_indices[0]

        dense_map = {}

        for score, idx in zip(
            dense_scores,
            dense_indices,
        ):

            if idx >= 0:
                dense_map[int(idx)] = float(score)

        # ---------------------------------------------------------
        # BM25
        # ---------------------------------------------------------

        tokenized_query = self.tokenize(query)

        bm25_scores = self.bm25.get_scores(
            tokenized_query
        )

        # Only consider strong BM25 candidates.
        lexical_indices = np.argsort(
            bm25_scores
        )[::-1][:candidate_k]

        lexical_map = {
            int(idx): float(bm25_scores[idx])
            for idx in lexical_indices
        }

        # ---------------------------------------------------------
        # Combine candidate pools
        # ---------------------------------------------------------

        candidate_indices = (
            set(dense_map.keys())
            | set(lexical_map.keys())
        )

        candidate_indices = list(
            candidate_indices
        )

        dense_values = [
            dense_map.get(idx, 0.0)
            for idx in candidate_indices
        ]

        lexical_values = [
            lexical_map.get(idx, 0.0)
            for idx in candidate_indices
        ]

        dense_norm = self.normalize_scores(
            dense_values
        )

        lexical_norm = self.normalize_scores(
            lexical_values
        )

        combined = (
            self.dense_weight * dense_norm
            +
            self.lexical_weight * lexical_norm
        )

        ranked = sorted(
            zip(
                candidate_indices,
                combined,
            ),
            key=lambda x: x[1],
            reverse=True,
        )

        # ---------------------------------------------------------
        # Return results, avoiding multiple chunks from one paper
        # when possible.
        # ---------------------------------------------------------

        results = []

        seen_documents = set()

        for idx, score in ranked:

            chunk = self.chunks[idx]

            document_id = chunk[
                "document_id"
            ]

            if document_id in seen_documents:
                continue

            seen_documents.add(
                document_id
            )

            result = dict(chunk)

            result["score"] = float(score)

            results.append(result)

            if len(results) >= k:
                break

        return results


if __name__ == "__main__":

    retriever = HybridRetriever()

    while True:

        query = input(
            "\nQuery (or quit): "
        ).strip()

        if query.lower() in {
            "quit",
            "exit",
        }:
            break

        results = retriever.search(
            query,
            k=5,
        )

        for i, result in enumerate(
            results,
            start=1,
        ):

            print()
            print("=" * 80)
            print(f"[{i}] {result['score']:.4f}")
            print(result["title"])
            print(
                f"Document: {result['document_id']}"
            )
            print(
                f"Section:  {result['section']}"
            )
            print()
            print(
                result["text"][:1000]
            )
