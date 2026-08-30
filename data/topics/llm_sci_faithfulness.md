---
id: llm-sci-faithfulness
field: nlp
title: Faithfulness evaluation of LLM-generated scientific paper summaries under a limited API and annotation budget
keywords:
  - large language models
  - summarization
  - faithfulness
  - scientific NLP
budget:
  gpu: "1x A100 40GB (shared, not dedicated)"
  gpu_hours: 20
  calendar_weeks: 6
  api_usd: 80
  annotator_hours: 16
  notes: "API spend is the binding constraint. Human annotation is only for a small calibration set, not for labeling a new benchmark at scale. Prefer public scientific summarization data (e.g. arXiv papers with abstracts, SciTLDR, or similar public corpora). Do not scrape paywalled PDFs."
---

# Research background

LLMs can produce fluent summaries of scientific papers, but fluency is a poor proxy for **faithfulness**: summaries may invent numbers, misattribute findings, drop crucial limitations, or merge results from related work into the paper’s claims. For a small lab, the question is how to **detect or reduce** these errors when both API spend and expert annotation hours are tightly capped.

## Related work and limitations

- **QAGS / QA-based factuality** (Wang et al., 2020 and follow-ups) convert summary claims into questions and check answers against the source. Limitation: question generation quality dominates; scientific claims with numbers, hedges, and citations are poorly handled by general QA pipelines.
- **FActScore** (Min et al., 2023) decomposes generations into atomic facts and verifies them against a knowledge source. Limitation: designed around biography-style facts and Wikipedia; scientific papers have different atomic units (method details, effect sizes, conditions).
- **ALCE** (Gao et al., 2023) evaluates citation-supported generation. Limitation: citation presence is not the same as faithful reading of the cited paper; a summary can cite the right paper and still distort the result.
- **G-Eval / LLM-as-judge** factuality prompts are cheap but unstable, and they can share the same hallucination modes as the summarizer if the judge model is similar.
- **NLI-based summarization metrics** (e.g. SummaC, Laban et al., 2022) work better on news than on long, equation-heavy scientific text and often require sentence-level alignment that breaks on abstractive scientific summaries.

## Open problems in this topic

1. A faithfulness protocol for **scientific** summaries whose atomic units include numbers, conditions, and hedges, not just named entities.
2. How much a tiny expert calibration set (≤16 annotator hours) can actually buy when tuning or checking an automatic metric.
3. Cost-quality trade-off: local small models vs. a few expensive API calls for verification.
4. Distinguishing **unsupported additions**, **source contradictions**, and **critical omissions** (especially omitted limitations).

## Allowed evaluation setting

- Input: publicly available paper text (arXiv HTML/TeX or public summarization datasets). Abstracts may be used as references but are not assumed to be complete faithfulness oracles.
- Systems under test may include prompting a public API model **within the $80 cap** and/or a local model that fits the 20 GPU-hour budget.
- A meaningful verification must include at least one strong automatic baseline (e.g. an NLI or QA factuality metric) and a small human study on a pre-registered slice, not only LLM-as-judge scores.

## Out of scope

Building a large expert-labeled scientific faithfulness benchmark, training a new LLM from scratch, or any design that needs more than $80 API or 16 annotator hours to produce the main result.
