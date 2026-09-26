#!/usr/bin/env python3
"""
Build a small open-access chemistry corpus from Europe PMC.

Outputs:
    chemistry_corpus/
      documents/
        *.txt
      documents.jsonl
      queries.jsonl
      README.md

Requirements:
    pip install requests beautifulsoup4 lxml tqdm
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OUTPUT_DIR = Path("chemistry_corpus")
DOCUMENT_DIR = OUTPUT_DIR / "documents"

TARGET_DOCUMENTS = 60

# Europe PMC query. OPEN_ACCESS:Y ensures that we target OA material.
SEARCH_QUERY = """
OPEN_ACCESS:Y AND
(
    chemistry OR
    catalysis OR
    synthesis OR
    polymer OR
    photocatalysis OR
    electrochemistry OR
    "organic chemistry" OR
    "materials chemistry"
)
AND FIRST_PDATE:[2015-01-01 TO 2026-12-31]
"""

EUROPE_PMC_SEARCH = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
EUROPE_PMC_FULLTEXT = (
    "https://www.ebi.ac.uk/europepmc/webservices/rest/"
    "{pmcid}/fullTextXML"
)

HEADERS = {
    "User-Agent": "chemistry-semantic-search-evaluation/1.0 "
                  "(research corpus downloader)"
}

# Avoid overloading the API.
REQUEST_DELAY = 0.25


# ---------------------------------------------------------------------------
# Chemistry-oriented query set
# ---------------------------------------------------------------------------

# These are deliberately phrased differently from paper titles.
# They can later be replaced/expanded with manually judged queries.
SEED_QUERIES = [
    {
        "query": "light driven carbon and nitrogen functionalization of alkenes",
        "topics": ["photochemistry", "organic synthesis"],
    },
    {
        "query": "palladium catalyzed carbon carbon bond formation",
        "topics": ["catalysis", "organic synthesis"],
    },
    {
        "query": "methods for controlled polymer sequence structures",
        "topics": ["polymer chemistry"],
    },
    {
        "query": "ring opening polymerization catalysts for biodegradable polymers",
        "topics": ["polymer chemistry", "catalysis"],
    },
    {
        "query": "photocatalysts used to transform organic molecules using visible light",
        "topics": ["photochemistry", "catalysis"],
    },
    {
        "query": "electrochemical methods for detecting biological molecules",
        "topics": ["electrochemistry", "analytical chemistry"],
    },
    {
        "query": "mass spectrometry techniques for studying electrochemical reactions",
        "topics": ["analytical chemistry", "electrochemistry"],
    },
    {
        "query": "biocatalysts used for synthetic organic chemistry",
        "topics": ["biocatalysis", "organic synthesis"],
    },
    {
        "query": "mechanochemical degradation and recycling of polymers",
        "topics": ["polymer chemistry", "mechanochemistry"],
    },
    {
        "query": "polymer based materials for controlled drug delivery",
        "topics": ["polymer chemistry", "medicinal chemistry"],
    },
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def normalize_whitespace(text: str) -> str:
    """Normalize whitespace without destroying paragraph boundaries."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def clean_text(text: str) -> str:
    """
    Remove common XML/HTML artifacts while retaining readable chemistry text.
    """
    text = BeautifulSoup(text, "lxml").get_text(" ", strip=True)

    # Unicode normalization-ish cleanup.
    replacements = {
        "\u00a0": " ",
        "\u2013": "-",
        "\u2014": "-",
        "\u2212": "-",
        "\u00b0": "°",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return normalize_whitespace(text)


def extract_section_text(section) -> str:
    """
    Recursively extract paragraph text from an XML section.
    """
    paragraphs = []

    for p in section.find_all("p"):
        text = p.get_text(" ", strip=True)
        if text:
            paragraphs.append(text)

    return "\n\n".join(paragraphs)


def parse_article_xml(xml: str) -> Optional[Dict]:
    """
    Extract title, abstract, sections, authors, DOI and license from
    Europe PMC full-text XML.
    """
    soup = BeautifulSoup(xml, "xml")

    article = soup.find("article")
    if article is None:
        return None

    # ---- Title ------------------------------------------------------------

    title_node = soup.find("article-title")
    title = title_node.get_text(" ", strip=True) if title_node else ""

    # ---- Abstract ----------------------------------------------------------

    abstract_parts = []

    for abstract in soup.find_all("abstract"):
        text = abstract.get_text(" ", strip=True)
        if text:
            abstract_parts.append(text)

    abstract = "\n\n".join(abstract_parts)

    # ---- Authors -----------------------------------------------------------

    authors = []

    for contrib in soup.find_all("contrib"):
        if contrib.get("contrib-type") != "author":
            continue

        surname = contrib.find("surname")
        given = contrib.find("given-names")

        if surname:
            name = surname.get_text(" ", strip=True)
            if given:
                name = f"{given.get_text(' ', strip=True)} {name}"
            authors.append(name)

    # ---- DOI ----------------------------------------------------------------

    doi = ""

    for article_id in soup.find_all("article-id"):
        if article_id.get("pub-id-type") == "doi":
            doi = article_id.get_text(strip=True)
            break

    # ---- License -----------------------------------------------------------

    license_text = ""

    license_node = soup.find("license")
    if license_node:
        license_text = license_node.get_text(" ", strip=True)

    # ---- Publication date --------------------------------------------------

    year = None

    for year_node in soup.find_all("year"):
        try:
            candidate = int(year_node.get_text(strip=True))
        except ValueError:
            continue

        if 1900 <= candidate <= 2100:
            year = candidate
            break

    # ---- Sections -----------------------------------------------------------

    sections = []

    body = soup.find("body")

    if body:
        for sec in body.find_all("sec", recursive=False):
            title_node = sec.find("title", recursive=False)

            section_title = (
                title_node.get_text(" ", strip=True)
                if title_node
                else "Section"
            )

            section_text = extract_section_text(sec)

            if section_text:
                sections.append(
                    {
                        "title": section_title,
                        "text": section_text,
                    }
                )

    # Some XML documents have nested sections rather than direct children.
    if not sections and body:
        for sec in body.find_all("sec"):
            title_node = sec.find("title", recursive=False)

            section_title = (
                title_node.get_text(" ", strip=True)
                if title_node
                else "Section"
            )

            section_text = extract_section_text(sec)

            if section_text:
                sections.append(
                    {
                        "title": section_title,
                        "text": section_text,
                    }
                )

    # ---- Build clean document text -----------------------------------------

    chunks = []

    if abstract:
        chunks.append("ABSTRACT\n" + clean_text(abstract))

    for section in sections:
        chunks.append(
            f"{section['title'].upper()}\n"
            + clean_text(section["text"])
        )

    full_text = "\n\n".join(chunks)

    return {
        "title": clean_text(title),
        "abstract": clean_text(abstract),
        "authors": authors,
        "doi": doi,
        "year": year,
        "license": clean_text(license_text),
        "sections": sections,
        "text": full_text,
    }


def europe_pmc_search(
    query: str,
    page_size: int = 100,
) -> List[Dict]:
    """Search Europe PMC and return article records."""

    params = {
        "query": query,
        "format": "json",
        "pageSize": page_size,
        "resultType": "core",
    }

    response = requests.get(
        EUROPE_PMC_SEARCH,
        params=params,
        headers=HEADERS,
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()

    return data.get("resultList", {}).get("result", [])


def download_xml(pmcid: str) -> Optional[str]:
    """Download full-text XML for a PMC article."""

    url = EUROPE_PMC_FULLTEXT.format(pmcid=pmcid)

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30,
    )

    if response.status_code != 200:
        return None

    return response.text


def article_is_usable(record: Dict) -> bool:
    """
    Filter out records that aren't useful for a local semantic-search corpus.
    """

    pmcid = record.get("pmcid")

    if not pmcid:
        return False

    # We want substantial full-text documents rather than tiny notices.
    title = record.get("title", "")

    if not title or len(title) < 15:
        return False

    return True


def make_document_id(index: int) -> str:
    return f"paper_{index:03d}"


# ---------------------------------------------------------------------------
# Main corpus builder
# ---------------------------------------------------------------------------

def main():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DOCUMENT_DIR.mkdir(parents=True, exist_ok=True)

    print("Searching Europe PMC...")
    print()

    records = europe_pmc_search(
        SEARCH_QUERY,
        page_size=200,
    )

    print(f"Search returned {len(records)} candidate records.")

    # Deduplicate by PMCID.
    unique = {}

    for record in records:
        pmcid = record.get("pmcid")

        if pmcid:
            unique[pmcid] = record

    records = list(unique.values())

    # Filter obvious non-usable records.
    records = [
        r for r in records
        if article_is_usable(r)
    ]

    print(f"Usable candidates: {len(records)}")
    print()

    metadata_records = []

    document_index = 1

    for record in tqdm(
        records,
        desc="Downloading full text",
    ):

        if document_index > TARGET_DOCUMENTS:
            break

        pmcid = record["pmcid"]

        xml = download_xml(pmcid)

        time.sleep(REQUEST_DELAY)

        if not xml:
            continue

        parsed = parse_article_xml(xml)

        if not parsed:
            continue

        # Require meaningful full text.
        if len(parsed["text"]) < 3000:
            continue

        doc_id = make_document_id(document_index)

        txt_path = DOCUMENT_DIR / f"{doc_id}.txt"

        txt_path.write_text(
            parsed["text"],
            encoding="utf-8",
        )

        # Europe PMC URL.
        source_url = (
            f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/"
        )

        metadata = {
            "id": doc_id,
            "title": parsed["title"],
            "authors": parsed["authors"],
            "year": parsed["year"],
            "doi": parsed["doi"],
            "pmcid": pmcid,
            "source": "Europe PMC / PubMed Central",
            "url": source_url,
            "license": parsed["license"],
            "text_path": str(txt_path),
            "character_count": len(parsed["text"]),
            "section_count": len(parsed["sections"]),
        }

        metadata_records.append(metadata)

        document_index += 1

    # -----------------------------------------------------------------------
    # Write metadata.jsonl
    # -----------------------------------------------------------------------

    metadata_path = OUTPUT_DIR / "documents.jsonl"

    with metadata_path.open("w", encoding="utf-8") as f:
        for record in metadata_records:
            f.write(json.dumps(
                record,
                ensure_ascii=False,
            ) + "\n")

    # -----------------------------------------------------------------------
    # Create starter queries
    # -----------------------------------------------------------------------

    query_records = []

    for i, item in enumerate(SEED_QUERIES, start=1):
        query_records.append({
            "query_id": f"q_{i:03d}",
            "query": item["query"],
            "topics": item["topics"],
            "relevant": [],
        })

    # CHANGED: Constructed separately using AI
    # queries_path = OUTPUT_DIR / "queries.jsonl"

    # with queries_path.open("w", encoding="utf-8") as f:
    #     for record in query_records:
    #         f.write(json.dumps(
    #             record,
    #             ensure_ascii=False,
    #         ) + "\n")

    # -----------------------------------------------------------------------
    # README
    # -----------------------------------------------------------------------

    readme = f"""# Chemistry Semantic Search Corpus

Generated from Europe PMC open-access full text.

Documents: {len(metadata_records)}

## Files

- `documents.jsonl` - document metadata
- `documents/` - cleaned full-text documents
- `queries.jsonl` - starter semantic-search queries

## Important

Each document retains its original PMCID, DOI, source URL,
and license information where available.

Check the license for each document before redistributing
the corpus outside your own evaluation environment.

## Suggested evaluation

Create relevance judgments in `queries.jsonl`:

    {{
      "query_id": "q_001",
      "query": "...",
      "relevant": ["paper_003", "paper_017"]
    }}

Then evaluate:

- Recall@5
- Recall@10
- MRR
- nDCG@10
"""

    (OUTPUT_DIR / "README.md").write_text(
        readme,
        encoding="utf-8",
    )

    print()
    print("=" * 60)
    print("Corpus complete")
    print("=" * 60)
    print(f"Documents:  {len(metadata_records)}")
    print(f"Output:     {OUTPUT_DIR.resolve()}")
    print(f"Metadata:   {metadata_path}")
    print(f"Queries:    {queries_path}")
    print()

    if len(metadata_records) < TARGET_DOCUMENTS:
        print(
            f"WARNING: only obtained {len(metadata_records)} "
            f"documents out of requested {TARGET_DOCUMENTS}."
        )
        print(
            "Try broadening SEARCH_QUERY or increasing page_size."
        )


if __name__ == "__main__":
    main()
