#!/usr/bin/env python3

import argparse
import json
import re
from pathlib import Path

import requests

from src.answer import OLLAMA_MODEL, answer_question, extract_citations
from src.retrieve import HybridRetriever


ROOT = Path(__file__).resolve().parent
DEFAULT_CASES = ROOT / "evaluation" / "e2e_cases.jsonl"
DEFAULT_OUTPUT = ROOT / "evaluation" / "e2e_results.json"
DEFAULT_OLLAMA_URL = "http://localhost:11434/api/generate"
ABSTENTION_PATTERN = re.compile(
    r"\b(not contained|does not contain|do not contain|doesn't contain|"
    r"not provide|does not provide|do not provide|not report|does not report|"
    r"cannot answer|can't answer|insufficient evidence|unable to answer|"
    r"not enough information|not available|abstain)\b",
    re.IGNORECASE,
)


def load_cases(path):
    cases = []

    with path.open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            if not line.strip():
                continue

            case = json.loads(line)
            required = {
                "case_id",
                "query",
                "should_abstain",
                "expected_document_ids",
                "reference_answer",
            }
            missing = required - case.keys()
            if missing:
                raise ValueError(
                    f"{path}:{line_number}: missing fields {sorted(missing)}"
                )
            if case["should_abstain"] == bool(case["expected_document_ids"]):
                raise ValueError(
                    f"{case['case_id']}: abstention and expected documents conflict"
                )
            cases.append(case)

    if not cases:
        raise ValueError(f"No evaluation cases found in {path}")

    return cases


def judge_answer(
    case,
    answer,
    results,
    model,
    ollama_url,
):
    sources = "\n\n".join(
        f"[{index}] {result['document_id']} | {result['title']}\n{result['text']}"
        for index, result in enumerate(results, start=1)
    )

    prompt = f"""You are a strict evaluator for a retrieval-augmented chemistry assistant.
Judge only from the supplied excerpts and reference answer. Do not use outside knowledge.
Return one JSON object with boolean fields correctness, groundedness, abstained,
citation_support, and a short string field reason.

Rules:
- correctness: for answerable cases, the answer accurately conveys the reference answer's key facts; for unanswerable cases, it correctly declines to answer.
- groundedness: every factual claim in the answer is supported by the supplied excerpts. An explicit abstention with no factual claims is grounded.
- abstained: true only if the answer clearly says the supplied evidence is insufficient or the answer is unavailable.
- citation_support: factual claims use citations that refer to supplied excerpts supporting those claims. An abstention without factual claims passes.

QUESTION: {case['query']}
EXPECTED ABSTENTION: {case['should_abstain']}
REFERENCE ANSWER: {case['reference_answer']}

SUPPLIED EXCERPTS:
{sources or '(none)'}

ASSISTANT ANSWER:
{answer}
"""

    response = requests.post(
        ollama_url,
        json={
            "model": model,
            "prompt": prompt,
            "format": "json",
            "stream": False,
            "options": {"temperature": 0.0},
        },
        timeout=180,
    )
    response.raise_for_status()
    judged = json.loads(response.json()["response"])

    boolean_fields = (
        "correctness",
        "groundedness",
        "abstained",
        "citation_support",
    )
    if any(not isinstance(judged.get(field), bool) for field in boolean_fields):
        raise ValueError(f"Judge returned invalid JSON fields: {judged}")

    return judged


def average(values):
    return sum(values) / len(values) if values else None


def evaluate_case(case, retriever, args):
    results = retriever.search(
        case["query"],
        k=args.top_k,
        candidate_k=args.candidate_k,
    )
    generated = answer_question(
        case["query"],
        results,
        model=args.answer_model,
        ollama_url=args.ollama_url,
    )

    expected = set(case["expected_document_ids"])
    retrieved = {result["document_id"] for result in results}
    cited_numbers = extract_citations(generated["answer"])
    citations_valid = (
        all(1 <= number <= len(results) for number in cited_numbers)
        and (case["should_abstain"] or bool(cited_numbers))
    )
    cited_documents = {
        results[number - 1]["document_id"]
        for number in cited_numbers
        if 1 <= number <= len(results)
    }
    retrieval_recall = (
        len(expected & retrieved) / len(expected)
        if expected
        else None
    )
    citation_recall = (
        len(expected & cited_documents) / len(expected)
        if expected
        else None
    )

    record = {
        "case_id": case["case_id"],
        "query": case["query"],
        "should_abstain": case["should_abstain"],
        "expected_document_ids": sorted(expected),
        "retrieved_document_ids": [
            result["document_id"] for result in results
        ],
        "retrieval_recall": retrieval_recall,
        "cited_document_ids": sorted(cited_documents),
        "citation_recall": citation_recall,
        "citations_valid": citations_valid,
        "abstained_by_pattern": bool(ABSTENTION_PATTERN.search(generated["answer"])),
        "answer": generated["answer"],
    }

    if args.judge:
        try:
            record["judge"] = judge_answer(
                case,
                generated["answer"],
                results,
                args.judge_model,
                args.ollama_url,
            )
        except (requests.RequestException, ValueError, KeyError, json.JSONDecodeError) as error:
            record["judge_error"] = str(error)

    return record


def summarize(records):
    judged = [record["judge"] for record in records if "judge" in record]
    abstention_accuracy = [
        judge["abstained"] == record["should_abstain"]
        for record in records
        for judge in [record.get("judge")]
        if judge is not None
    ]
    pattern_abstention_accuracy = [
        record["abstained_by_pattern"] == record["should_abstain"]
        for record in records
    ]
    return {
        "cases": len(records),
        "answerable_cases": sum(not record["should_abstain"] for record in records),
        "unanswerable_cases": sum(record["should_abstain"] for record in records),
        "retrieval_recall": average(
            [record["retrieval_recall"] for record in records if record["retrieval_recall"] is not None]
        ),
        "citation_recall": average(
            [record["citation_recall"] for record in records if record["citation_recall"] is not None]
        ),
        "valid_citation_rate": average(
            [float(record["citations_valid"]) for record in records]
        ),
        "judge_correctness_rate": average(
            [float(judge["correctness"]) for judge in judged]
        ),
        "judge_groundedness_rate": average(
            [float(judge["groundedness"]) for judge in judged]
        ),
        "judge_citation_support_rate": average(
            [
                float(judge["citation_support"])
                for record in records
                for judge in [record.get("judge")]
                if judge is not None and not judge["abstained"]
            ]
        ),
        "judge_abstention_accuracy": average(
            [float(value) for value in abstention_accuracy]
        ),
        "pattern_abstention_accuracy": average(
            [float(value) for value in pattern_abstention_accuracy]
        ),
        "judge_errors": sum("judge_error" in record for record in records),
    }


def parse_args():
    parser = argparse.ArgumentParser(
        description="Evaluate retrieval and generated answers end to end using Ollama."
    )
    parser.add_argument("--data", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--candidate-k", type=int, default=20)
    parser.add_argument("--answer-model", default=OLLAMA_MODEL)
    parser.add_argument("--judge-model", default=OLLAMA_MODEL)
    parser.add_argument("--ollama-url", default=DEFAULT_OLLAMA_URL)
    parser.add_argument(
        "--no-judge",
        action="store_false",
        dest="judge",
        help="Skip the second Ollama call used to judge response quality.",
    )
    parser.set_defaults(judge=True)
    return parser.parse_args()


def main():
    args = parse_args()
    if args.top_k <= 0 or args.candidate_k <= 0:
        raise SystemExit("--top-k and --candidate-k must be positive")

    cases = load_cases(args.data)
    retriever = HybridRetriever()
    records = []

    for case in cases:
        record = evaluate_case(case, retriever, args)
        records.append(record)
        print(f"\n{record['case_id']}: {record['query']}")
        print(f"  retrieved: {', '.join(record['retrieved_document_ids']) or '(none)'}")
        print(f"  answer: {record['answer']}")
        if "judge" in record:
            print(f"  judge: {record['judge']}")
        elif "judge_error" in record:
            print(f"  judge error: {record['judge_error']}")

    summary = summarize(records)
    output = {
        "answer_model": args.answer_model,
        "judge_model": args.judge_model if args.judge else None,
        "summary": summary,
        "results": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print("\nSummary")
    for name, value in summary.items():
        display = f"{value:.3f}" if isinstance(value, float) else value
        print(f"  {name}: {display}")
    print(f"\nSaved detailed results to {args.output}")


if __name__ == "__main__":
    main()
