#!/usr/bin/env python3

import re
from typing import List

import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.1:8b"


SYSTEM_PROMPT = """
You are a research knowledge assistant for scientists.

Your job is to answer questions ONLY from the supplied
document excerpts.

Rules:

1. Do not use outside knowledge.
2. Every factual claim must be supported by one or more
   supplied sources.
3. Put citations immediately after the claims they support.
4. Use citation numbers such as [1], [2], [3].
5. If the supplied evidence does not answer the question,
   explicitly say that the answer is not contained in the
   supplied corpus.
6. Do not fill gaps using general scientific knowledge.
7. If only part of a question can be answered, answer that
   part and explicitly identify what is missing.
8. Do not invent citations.
9. Do not cite a source unless its supplied text actually
   supports the claim.
10. Prefer precise scientific language.

Your answer should be concise but useful.
"""


def build_context(results: List[dict]):

    sections = []

    for i, result in enumerate(
        results,
        start=1,
    ):

        sections.append(
            f"""
SOURCE [{i}]
Document ID: {result["document_id"]}
Title: {result["title"]}
Section: {result["section"]}
Year: {result.get("year")}
Source URL: {result.get("source_url")}

TEXT:
{result["text"]}
"""
        )

    return "\n".join(sections)


def build_prompt(question, results):

    context = build_context(results)

    return f"""
{SYSTEM_PROMPT}

QUESTION:
{question}

SUPPLIED SOURCES:
{context}

Answer the question using ONLY the supplied sources.

Remember:
- cite factual claims
- do not fabricate
- explicitly abstain if evidence is insufficient
"""


def call_ollama(
    prompt,
    model=OLLAMA_MODEL,
    ollama_url=OLLAMA_URL,
):
    response = requests.post(
        ollama_url,
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.0,
            },
        },
        timeout=180,
    )

    response.raise_for_status()

    return response.json()["response"]


def extract_citations(answer):

    matches = re.findall(
        r"\[(\d+)\]",
        answer,
    )

    return sorted(
        set(int(x) for x in matches)
    )


def answer_question(
    question,
    results,
    model=OLLAMA_MODEL,
    ollama_url=OLLAMA_URL,
):

    prompt = build_prompt(
        question,
        results,
    )

    answer = call_ollama(
        prompt,
        model=model,
        ollama_url=ollama_url,
    )

    citation_numbers = extract_citations(
        answer
    )

    citations = []

    for number in citation_numbers:

        if 1 <= number <= len(results):

            result = results[number - 1]

            citations.append({
                "citation": number,
                "document_id": result[
                    "document_id"
                ],
                "title": result[
                    "title"
                ],
                "section": result[
                    "section"
                ],
                "source_url": result.get(
                    "source_url"
                ),
            })

    return {
        "answer": answer,
        "citations": citations,
        "evidence": results,
    }

