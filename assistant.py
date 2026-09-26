#!/usr/bin/env python3

from src.retrieve import HybridRetriever
from src.answer import answer_question


def print_sources(citations):

    if not citations:
        return

    print()
    print("Sources")
    print("-------")

    for citation in citations:

        print(
            f"[{citation['citation']}] "
            f"{citation['title']}"
        )

        print(
            f"    Document: "
            f"{citation['document_id']}"
        )

        if citation.get("section"):
            print(
                f"    Section: "
                f"{citation['section']}"
            )

        if citation.get("source_url"):
            print(
                f"    URL: "
                f"{citation['source_url']}"
            )

        print()


def main():

    print()
    print("=" * 70)
    print("Research Knowledge Assistant")
    print("=" * 70)
    print()
    print(
        "Ask questions about the supplied chemistry corpus."
    )
    print(
        "Type 'quit' to exit."
    )
    print()

    retriever = HybridRetriever()

    while True:

        question = input(
            "\n\nQuestion> "
        ).strip()

        if question.lower() in {
            "quit",
            "exit",
        }:
            break

        if not question:
            continue

        print()
        print("Searching...")

        results = retriever.search(
            question,
            k=5,
            candidate_k=20,
        )

        if not results:
            print(
                "\nI couldn't find relevant "
                "material in the corpus."
            )
            continue

        # TODO - confidence gating
        # We can eliminate results based on scientists feedback or eval iterations.
        # if not results or results[0]["score"] < 0.20:
        #     print()
        #     print(
        #         "I couldn't find sufficient evidence "
        #         "in the supplied corpus to answer that."
        #     )
        #     continue

        result = answer_question(
            question,
            results,
        )

        print()
        print("Answer")
        print("------")
        print(result["answer"])

        print_sources(
            result["citations"]
        )


if __name__ == "__main__":
    main()
