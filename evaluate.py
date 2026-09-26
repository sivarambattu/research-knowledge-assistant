#!/usr/bin/env python3

import json
import math
from pathlib import Path

import numpy as np

from src.retrieve import HybridRetriever


QUERY_FILE = Path(
    "chemistry_corpus/queries.jsonl"
)


def load_queries():

    queries = []

    with QUERY_FILE.open(
        encoding="utf-8"
    ) as f:

        for line in f:

            if line.strip():
                queries.append(
                    json.loads(line)
                )

    return queries


def precision_at_k(results, relevant, k):

    if k <= 0:
        return 0.0

    relevant = set(relevant)

    retrieved = [
        result["document_id"]
        for result in results[:k]
    ]

    if not retrieved:
        return 0.0

    hits = sum(
        1
        for document_id in retrieved
        if document_id in relevant
    )

    return hits / len(retrieved)


def recall_at_k(results, relevant, k):

    relevant = set(relevant)

    if not relevant:
        return None

    retrieved = {
        result["document_id"]
        for result in results[:k]
    }

    return len(
        retrieved & relevant
    ) / len(relevant)


def reciprocal_rank(results, relevant):

    relevant = set(relevant)

    for rank, result in enumerate(
        results,
        start=1,
    ):

        if result["document_id"] in relevant:
            return 1.0 / rank

    return 0.0


def average_precision(
    results,
    relevant,
):

    relevant = set(relevant)

    if not relevant:
        return None

    hits = 0
    precision_sum = 0.0

    for rank, result in enumerate(
        results,
        start=1,
    ):

        if result["document_id"] in relevant:

            hits += 1

            precision_sum += (
                hits / rank
            )

    if hits == 0:
        return 0.0

    return (
        precision_sum
        / min(len(relevant), len(results))
    )


def ndcg_at_k(
    results,
    relevant,
    k,
):

    relevant = set(relevant)

    dcg = 0.0

    for rank, result in enumerate(
        results[:k],
        start=1,
    ):

        if result["document_id"] in relevant:

            dcg += (
                1.0
                / math.log2(rank + 1)
            )

    ideal_relevant = min(
        len(relevant),
        k,
    )

    if ideal_relevant == 0:
        return None

    idcg = sum(
        1.0 / math.log2(rank + 1)
        for rank in range(
            1,
            ideal_relevant + 1,
        )
    )

    return dcg / idcg


def evaluate_abstention(
    retriever,
    queries,
    threshold=0.20,
):

    abstention_queries = [
        query
        for query in queries
        if query.get("type") == "unanswerable"
    ]

    if not abstention_queries:
        return

    correct = 0

    print()
    print("=" * 70)
    print("ABSTENTION EVALUATION")
    print("=" * 70)

    for query in abstention_queries:

        results = retriever.search(
            query["query"],
            k=5,
            candidate_k=20,
        )

        if not results:
            should_abstain = True

        else:
            should_abstain = (
                results[0]["score"]
                < threshold
            )

        if should_abstain:
            correct += 1

        print()
        print(query["query"])
        print(
            "Top retrieval score:",
            (
                f"{results[0]['score']:.3f}"
                if results
                else "none"
            ),
        )
        print(
            "Correct abstention:",
            should_abstain,
        )

    accuracy = (
        correct / len(abstention_queries)
    )

    print()
    print(
        f"Abstention accuracy: "
        f"{accuracy:.3f}"
    )


def evaluate_answerable(
    retriever,
    queries,
):

    rows = []

    for query in queries:

        relevant = query.get(
            "relevant",
            [],
        )

        # Skip abstention questions here.
        if not relevant:
            continue

        results = retriever.search(
            query["query"],
            k=10,
            candidate_k=30,
        )

        rows.append({
            "query_id": query["query_id"],

            "precision@3":
                precision_at_k(
                    results,
                    relevant,
                    3,
                ),

            "precision@5":
                precision_at_k(
                    results,
                    relevant,
                    5,
                ),

            "recall@5":
                recall_at_k(
                    results,
                    relevant,
                    5,
                ),

            "recall@10":
                recall_at_k(
                    results,
                    relevant,
                    10,
                ),

            "MRR":
                reciprocal_rank(
                    results,
                    relevant,
                ),

            "MAP":
                average_precision(
                    results,
                    relevant,
                ),

            "nDCG@5":
                ndcg_at_k(
                    results,
                    relevant,
                    5,
                ),

            "nDCG@10":
                ndcg_at_k(
                    results,
                    relevant,
                    10,
                ),
        })

    return rows


def print_results(rows):

    metrics = [
        "precision@3",
        "precision@5",
        "recall@5",
        "recall@10",
        "MRR",
        "MAP",
        "nDCG@5",
        "nDCG@10",
    ]

    print()
    print("=" * 70)
    print("RETRIEVAL EVALUATION")
    print("=" * 70)

    print(
        f"Evaluated queries: {len(rows)}"
    )

    print()

    for metric in metrics:

        values = [
            row[metric]
            for row in rows
            if row[metric] is not None
        ]

        if not values:
            continue

        print(
            f"{metric:<15} "
            f"{np.mean(values):.3f}"
        )


def save_results(rows):

    output = Path(
        "evaluation_results.json"
    )

    with output.open(
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            rows,
            f,
            indent=2,
        )

    print()
    print(
        f"Detailed results: {output}"
    )


def main():

    queries = load_queries()

    answerable = [
        query
        for query in queries
        if query.get("relevant")
    ]

    retriever = HybridRetriever()

    rows = evaluate_answerable(
        retriever,
        answerable,
    )

    print_results(rows)

    save_results(rows)

    evaluate_abstention(
        retriever,
        queries,
    )


if __name__ == "__main__":
    main()
