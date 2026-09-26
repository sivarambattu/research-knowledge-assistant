#!/usr/bin/env python3

import json
import re
from pathlib import Path

from tqdm import tqdm


CORPUS_DIR = Path("chemistry_corpus")
OUTPUT_DIR = Path("data")

OUTPUT_DIR.mkdir(exist_ok=True)

METADATA_FILE = CORPUS_DIR / "documents.jsonl"
OUTPUT_FILE = OUTPUT_DIR / "chunks.jsonl"

TARGET_WORDS = 400
OVERLAP_WORDS = 75


def load_metadata():
    documents = []

    with METADATA_FILE.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                documents.append(json.loads(line))

    return documents


def detect_sections(text):
    """
    The corpus generator puts section names in uppercase.

    This function uses those headings to preserve section metadata.
    """

    lines = text.splitlines()

    sections = []

    current_section = "Unknown"
    current_text = []

    known_headings = {
        "ABSTRACT",
        "INTRODUCTION",
        "BACKGROUND",
        "RESULTS",
        "RESULTS AND DISCUSSION",
        "DISCUSSION",
        "METHODS",
        "MATERIALS AND METHODS",
        "EXPERIMENTAL",
        "EXPERIMENTAL SECTION",
        "CONCLUSIONS",
        "CONCLUSION",
        "SUPPORTING INFORMATION",
    }

    for line in lines:

        stripped = line.strip()

        if not stripped:
            continue

        normalized = re.sub(
            r"[^A-Z0-9 ]",
            "",
            stripped.upper(),
        )

        if (
            normalized in known_headings
            or (
                len(stripped) < 100
                and stripped.isupper()
                and len(stripped.split()) <= 12
            )
        ):
            if current_text:
                sections.append({
                    "section": current_section,
                    "text": "\n".join(current_text),
                })

            current_section = stripped
            current_text = []

        else:
            current_text.append(stripped)

    if current_text:
        sections.append({
            "section": current_section,
            "text": "\n".join(current_text),
        })

    return sections


def paragraphs(text):
    return [
        p.strip()
        for p in re.split(r"\n\s*\n", text)
        if len(p.strip()) > 40
    ]


def chunk_section(text, target_words=TARGET_WORDS):
    """
    Paragraph-aware chunking with word-based overlap.
    """

    paras = paragraphs(text)

    chunks = []

    current = []
    current_words = 0

    for paragraph in paras:

        words = paragraph.split()

        if not words:
            continue

        if (
            current
            and current_words + len(words) > target_words
        ):
            chunks.append(" ".join(current))

            overlap = []
            overlap_count = 0

            for old in reversed(current):
                old_words = old.split()

                overlap.insert(0, old)

                overlap_count += len(old_words)

                if overlap_count >= OVERLAP_WORDS:
                    break

            current = overlap
            current_words = overlap_count

        current.append(paragraph)
        current_words += len(words)

    if current:
        chunks.append(" ".join(current))

    return chunks


def main():

    documents = load_metadata()

    all_chunks = []

    chunk_counter = 0

    for document in tqdm(
        documents,
        desc="Chunking documents",
    ):

        document_id = document["id"]

        text_path = Path(document["text_path"])

        text = text_path.read_text(
            encoding="utf-8",
        )

        sections = detect_sections(text)

        # Fallback if the section parser failed.
        if not sections:
            sections = [{
                "section": "Unknown",
                "text": text,
            }]

        for section_number, section in enumerate(sections):

            section_chunks = chunk_section(
                section["text"]
            )

            for chunk_number, chunk_text in enumerate(
                section_chunks
            ):

                if len(chunk_text.split()) < 50:
                    continue

                chunk_id = (
                    f"{document_id}_"
                    f"s{section_number:02d}_"
                    f"c{chunk_number:03d}"
                )

                record = {
                    "chunk_id": chunk_id,
                    "document_id": document_id,
                    "title": document["title"],
                    "year": document.get("year"),
                    "pmcid": document.get("pmcid"),
                    "doi": document.get("doi"),
                    "source_url": document.get("url"),
                    "license": document.get("license"),
                    "section": section["section"],
                    "text": chunk_text,
                }

                all_chunks.append(record)

                chunk_counter += 1

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as f:

        for chunk in all_chunks:
            f.write(
                json.dumps(
                    chunk,
                    ensure_ascii=False,
                )
                + "\n"
            )

    print()
    print(f"Documents: {len(documents)}")
    print(f"Chunks:    {len(all_chunks)}")
    print(f"Output:    {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
