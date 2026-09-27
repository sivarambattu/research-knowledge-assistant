# Prerequisites
- Python (Used version 3.14.3 for developing and testing this app)
- [Ollama](https://ollama.com/download)
- [UV](https://docs.astral.sh/uv/getting-started/installation/)

# Installation
Download ollama model used in the repo
```
ollama pull llama3.1:8b
```

Make sure ollama is running, if not it can be kicked off in a separate terminal
```
ollama serve
```

Setup application dependencies
```
uv sync
```

# Usage

## Running Knowledge assistant
The very first invocation of assistant might take some time while loading dependencies.
```
❯ uv run assistant.py 

======================================================================
Research Knowledge Assistant
======================================================================

Ask questions about the supplied chemistry corpus.
Type 'quit' to exit.

Question> How was the copper-pyrene MOF prepared and what reaction was it used to catalyze?

Searching...

Answer
------
The question is: How was the copper-pyrene MOF prepared and what reaction was it used to catalyze?

Unfortunately, the supplied sources do not provide a clear answer to this question. The sources mention the synthesis of various MOFs, including PCN-222 and HOF catalysts, but do not specifically describe the preparation of a copper-pyrene MOF.

Source [1] mentions the synthesis of a Cu-py MOF using an electrochemical procedure, but it does not provide a detailed description of the preparation method.

Source [2] discusses the synthesis of metalated PCN-222, but it does not mention the preparation of a copper-pyrene MOF.

Source [3] and Source [4] do not mention the copper-pyrene MOF at all.

Source [5] discusses the modification of MOFs, including halide doping and morphology engineering, but it does not provide information on the preparation of a copper-pyrene MOF.

Therefore, I must answer that the answer is not contained in the supplied corpus.

Sources
-------
[1] Electrochemical synthesis of Cu-pyrene MOF and its outstanding pohotoelectrocatalytic activity in hydrogen evolution reaction
    Document: paper_060
    Section: DISCUSSION
    URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC13378021/

[2] Facile and Fast
Microwave-Assisted Synthesis of Metalated
PCN-222 for Light-Driven Hydrogen Evolution Reaction
    Document: paper_020
    Section: INTRODUCTION
    URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC13520015/

[3] A Hydrogen Bonded Organic Framework Constructed from Mixed Valence Fe Clusters for Efficient H 2 O 2 Photosynthesis
    Document: paper_025
    Section: AUTHOR CONTRIBUTIONS
    URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC13530266/

[4] Mechanochemical optimization and scope of triple and multiple Sonogashira couplings of triethynylbenzene for conjugated porous polymer synthesis
    Document: paper_028
    Section: RESULTS AND DISCUSSION
    URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC13377219/

[5] Halide doping and morphology engineering in bismuth-based MOFs for enhanced water oxygen evolution
    Document: paper_047
    Section: INTRODUCTION
    URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC13233773/
```

```
Question> what catalyst was used for the polyester ring-opening polymerization

Searching...

Answer
------
The question is: what catalyst was used for the polyester ring-opening polymerization

Unfortunately, the supplied sources do not contain any information about the catalyst used for polyester ring-opening polymerization. The sources discuss various topics such as olefin metathesis, polymer-semiconductor composites, and porous organic polymers, but none of them mention ring-opening polymerization of polyester.

Therefore, I must explicitly abstain from answering the question, as the necessary information is not contained in the supplied corpus.
```
```
Question> what can you say about polymer-semiconductor composites

Searching...

Answer
------
Based on the supplied sources, here's what can be said about polymer-semiconductor composites:

1. **Photocatalytic activity enhancement**: The type of organic polymer incorporated into polymer-semiconductor composites plays a central role in their photocatalytic performance [1, Section: FACTORS GOVERNING PHOTOCATALYTIC ACTIVITY]. Conjugated and conducting polymers actively improve light absorption and charge separation [1, Section: BAND GAP ENGINEERING].
2. **Band gap engineering**: Organic polymers offer exceptional flexibility in band gap tuning through molecular design strategies, such as adjustment of conjugation length, donor-acceptor architecture, and functional group substitution [1, Section: BAND GAP ENGINEERING].
3. **Energy-level alignment**: Energy-level alignment between organic polymers and semiconductors is a decisive factor governing the efficiency of photocatalytic processes in polymer-semiconductor composites [1, Section: ENERGY-LEVEL ALIGNMENT].
4. **Interfacial charge transfer**: Interfacial charge transfer is a decisive process that influences the photocatalytic efficiency of organic polymer-semiconductor composites [1, Section: INTERFACIAL CHARGE TRANSFER].
5. **Morphology**: Morphology is a critical structural parameter that governs photocatalytic activity in organic polymer-semiconductor composites [1, Section: MORPHOLOGY].
6. **Surface area**: Surface area is a fundamental factor influencing photocatalytic activity in organic polymer-semiconductor composites [1, Section: SURFACE AREA].
7. **Porosity**: Porosity is a critical structural feature that governs mass transport, reactant diffusion, and product desorption in polymer-semiconductor photocatalysts [1, Section: POROSITY].
8. **Synthesis strategy**: The synthesis strategy of polymer-semiconductor composites is a key determinant of their photocatalytic performance [1, Section: SYNTHESIS STRATEGY].
9. **Recyclability**: The incorporation of organic polymers into semiconductor composites mitigates issues related to aggregation, leaching, or surface fouling during repeated use [1, Section: RECYCLABILITY].

The supplied sources do not provide information on the following aspects:

* The specific types of semiconductors used in polymer-semiconductor composites.
* The effects of different synthesis methods on the photocatalytic performance of polymer-semiconductor composites.
* The long-term stability of polymer-semiconductor composites under various environmental conditions.

References:

[1] Organic polymers tuned the photocatalytic activity of inorganic semiconductors in polymer-semiconductor composites: a critical review (2026)

[2] Next generation materials for environmental remediation through advanced mechanisms and future perspectives (2026)

[3] Homogeneous catalysis in continuous flow integrating photocatalysis, electrocatalysis, and automation technologies (2025)

[4] Additive Manufacturing in Organic Chemistry: From Synthesis to Sustainable Process Design (2026)

[5] Edward Sacher (1934-2023): Understanding Chemistry at the Interface (2026)

[6] Advanced nanocomposites for microplastic remediation: a critical review of materials, mechanisms, and scalability challenges (2026)

Sources
-------
[1] Organic polymers tuned the photocatalytic activity of inorganic semiconductors in polymer-semiconductor composites: a critical review
    Document: paper_042
    Section: FACTORS GOVERNING PHOTOCATALYTIC ACTIVITY
    URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC13325529/

[2] Next generation materials for environmental remediation through advanced mechanisms and future perspectives
    Document: paper_016
    Section: CLASSIFICATION OF NEXT-GENERATION MATERIALS FOR ENVIRONMENTAL APPLICATIONS
    URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC13498541/

[3] Homogeneous catalysis in continuous flow integrating photocatalysis, electrocatalysis, and automation technologies
    Document: paper_014
    Section: ACKNOWLEDGEMENTS
    URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC12594885/

[4] Additive Manufacturing in Organic Chemistry: From Synthesis to Sustainable Process Design
    Document: paper_019
    Section: 2. COMPARISON OF ADDITIVE MANUFACTURING TECHNOLOGIES FOR ORGANIC SYNTHESIS AND PROCESSING
    URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC13115704/

[5] Edward Sacher (1934-2023): Understanding Chemistry at the Interface
    Document: paper_012
    Section: 1. INTRODUCTION
    URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC13567493/

[6] Advanced nanocomposites for microplastic remediation: a critical review of materials, mechanisms, and scalability challenges
    Document: paper_039
    Section: ABSTRACT
    URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC13185801/
```
```
Question> how is the weather

Searching...

Answer
------
The question is "how is the weather".

Unfortunately, the supplied sources do not contain any information about the weather. The sources are related to chemistry, materials science, and research methods, but none of them mention the weather.

Therefore, I must answer: "The answer is not contained in the supplied corpus."

```

## Evaluate retriever with metrics
```
❯ uv run evaluate.py    

======================================================================
RETRIEVAL EVALUATION
======================================================================
Evaluated queries: 30

precision@3     0.344
precision@5     0.207
recall@5        1.000
recall@10       1.000
MRR             0.961
MAP             0.961
nDCG@5          0.971
nDCG@10         0.971

Detailed results: evaluation_results.json
```


## Evaluate end to end respsonse including LLM response
```
❯ uv run evaluate_e2e.py
....
....
Summary
  cases: 6
  answerable_cases: 4
  unanswerable_cases: 2
  retrieval_recall: 1.000
  citation_recall: 0.750
  valid_citation_rate: 0.833
  judge_correctness_rate: 0.500
  judge_groundedness_rate: 1.000
  judge_citation_support_rate: 1.000
  judge_abstention_accuracy: 0.500
  pattern_abstention_accuracy: 0.500
  judge_errors: 0

Saved detailed results to /Users/sivaram/Documents/career/companies/ohr/evaluation/e2e_results.json
```

# High level architecture

                     60 public documents
                              │
                              ▼
                    ┌─────────────────┐
                    │ Parse + chunk   │
                    │ section-aware   │
                    └────────┬────────┘
                             │
                  ┌──────────┴──────────┐
                  ▼                     ▼
             Sentence                BM25
            Transformer
                  │                     │
                  ▼                     ▼
                FAISS              lexical index
                  │                     │
                  └──────────┬──────────┘
                             ▼
                       hybrid ranking
                             │
                         top 5 chunks
                             │
                             ▼
                      retrieval gate
                       ↙           ↘
                   insufficient    sufficient
                       │              │
                       ▼              ▼
                   ABSTAIN           LLM
                                      │
                                      ▼
                              grounded response
                                      │
                                      ▼
                                  citations



- **Retrieval:** Hybrid dense + lexical retrieval is used because scientific documents contain both semantic concepts and exact identifiers such as chemical names, reagents, catalysts, and analytical methods.

- **Grounding:** The answer generator receives only retrieved document passages and is instructed to cite supporting passages for factual claims.

- **Abstention:** Questions for which the corpus provides insufficient evidence are explicitly declined rather than answered from model knowledge.

- **Evaluation:** Retrieval is measured using Recall, Precision, MRR, MAP, nDCG; generated answers are manually assessed for correctness, grounding, citation accuracy, and appropriate abstention. End to end evalutions are added as well

# AI Usage
- Initial exploration for alternatives with tradeoffs
- Finding documents for evaluation
- Coming up with eval set because I don't have chemistry domain expertise, I would've used scientists here to come up with better eval set
- To build both retriever evals as well as end to end workflow that includes LLM response generation.
- Most of the code has been generated by AI, I have reviewed it for functionality and tested manually.

# Decisions
- Limiting to PDFs from EUROPE_PMC in the prototype
- Ignoring images
- Chose open source local Model to avoid creating external accounts for trying out the demo.

# Improvements I would consider if I could spend more time
- Iterate on Embedding models (can use evaluate.py to iterate)
- Iterate on models for better and concise response generation (can use evaluate_e23.py to iterate)
- Clickable links in response not just the external links but to internal docs links for easier access
- Figure out what are the most relevant metrics for the scientists
    - They are okay with having more fuzzier matches, risk of noise
    - Only one or two relevant papers, risk of a miss

# Development details

Script to fetch documents and build corpus
```
❯ uv run python fetch_papers.py 
Searching Europe PMC...

Search returned 198 candidate records.
Usable candidates: 198

Downloading full text: 
```

Scripts to chunk and index corpus

```
❯ uv run python src/chunk.py
Chunking documents: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 60/60 [00:00<00:00, 715.55it/s]

Documents: 60
Chunks:    409
Output:    data/chunks.jsonl


❯ uv run python src/index.py 
Chunks: 409
Loading embedding model: sentence-transformers/all-MiniLM-L6-v2
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
modules.json: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 349/349 [00:00<00:00, 2.23MB/s]
...
....
2/112 [00:00<00:00, 316kB/s]
config.json: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 190/190 [00:00<00:00, 1.87MB/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 13/13 [00:02<00:00,  5.16it/s]

FAISS index created.
Vectors: 409
Dimensions: 384
```
