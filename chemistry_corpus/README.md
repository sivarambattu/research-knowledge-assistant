# Chemistry Semantic Search Corpus

Generated from Europe PMC open-access full text.

Documents: 60

## Files

- `documents.jsonl` - document metadata
- `documents/` - cleaned full-text documents
- `queries.jsonl` - starter semantic-search queries - this has been edited later using LLMs to build a golden set for retriever evaluation

## Important

Each document retains its original PMCID, DOI, source URL,
and license information where available.

Check the license for each document before redistributing
the corpus outside your own evaluation environment.

## Suggested evaluation

Create relevance judgments in `queries.jsonl`:

    {
      "query_id": "q_001",
      "query": "...",
      "relevant": ["paper_003", "paper_017"]
    }

Then evaluate:

- Recall@5
- Recall@10
- MRR
- nDCG@10









