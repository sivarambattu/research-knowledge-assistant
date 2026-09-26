# End-to-end evaluation

The small gold set in `e2e_cases.jsonl` tests retrieval, answer generation, citations, and abstention. Each case includes a reference answer for an optional LLM judge. The set is a smoke-test benchmark, not a substitute for expert review or a statistically representative evaluation set.

From the repository root, run:

```sh
uv run evaluate_e2e.py
```

This uses the local FAISS/BM25 index and `llama3.1:8b` through Ollama for both answer generation and judging. Start Ollama first and pull the model if needed. To avoid the second model call for judging:

```sh
uv run evaluate_e2e.py --no-judge
```

Useful options include `--data PATH`, `--output PATH`, `--answer-model MODEL`, `--judge-model MODEL`, `--ollama-url URL`, and `--top-k N`. The default output is `evaluation/e2e_results.json`; it contains the summary, retrieved and cited document IDs, generated response text, and per-case judge assessments.

The judge is itself an LLM and can be inconsistent. Treat its correctness, grounding, citation-support, and abstention metrics as review aids; inspect the saved answers and expand the gold set with domain-expert judgments before using scores to compare systems.
