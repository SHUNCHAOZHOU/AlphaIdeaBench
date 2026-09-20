---
id: survey_03_rag_systems
type: survey
field: llm_and_reasoning
title: "Retrieval-Augmented Generation for Large Language Models: A Survey"
arxiv_id: "2312.10997"
authors: "Yunfan Gao, Yun Xiong, Xinyu Gao et al."
source_url: "https://arxiv.org/abs/2312.10997"
pdf_url: "https://arxiv.org/pdf/2312.10997.pdf"
keywords:
  - retrieval-augmented-generation
  - rag
  - noise-robustness
  - multi-hop-retrieval
  - context-pollution
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---

# Retrieval-Augmented Generation for Large Language Models: A Survey

## 1. Verified Paper Identity & Links
- **Title**: Retrieval-Augmented Generation for Large Language Models: A Survey
- **Authors**: Yunfan Gao, Yun Xiong, Xinyu Gao et al.
- **arXiv Entry**: [https://arxiv.org/abs/2312.10997](https://arxiv.org/abs/2312.10997)
- **Full PDF**: [https://arxiv.org/pdf/2312.10997.pdf](https://arxiv.org/pdf/2312.10997.pdf)
- **Field**: llm_and_reasoning

## 2. Official Paper Abstract
Large Language Models (LLMs) showcase impressive capabilities but encounter challenges like hallucination, outdated knowledge, and non-transparent, untraceable reasoning processes. Retrieval-Augmented Generation (RAG) has emerged as a promising solution by incorporating knowledge from external databases. This enhances the accuracy and credibility of the generation, particularly for knowledge-intensive tasks, and allows for continuous knowledge updates and integration of domain-specific information. RAG synergistically merges LLMs&#39; intrinsic knowledge with the vast, dynamic repositories of external databases. This comprehensive review paper offers a detailed examination of the progression of RAG paradigms, encompassing the Naive RAG, the Advanced RAG, and the Modular RAG. It meticulously scrutinizes the tripartite foundation of RAG frameworks, which includes the retrieval, the generation and the augmentation techniques. The paper highlights the state-of-the-art technologies embedded in each of these critical components, providing a profound understanding of the advancements in RAG systems. Furthermore, this paper introduces up-to-date evaluation framework and benchmark. At the end, this article delineates the challenges currently faced and points out prospective avenues for research and development.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Distractor and Noise Sensitivity)**: Retrieved context containing subtle inaccuracies or irrelevant distractors severely degrades generation faithfulness.

- **Challenge 2 (Multi-Hop Dispersed Information Synthesis)**: Standard dense retrievers fetch isolated paragraphs, struggling to construct multi-document relational graphs.

- **Challenge 3 (Adaptive Retrieval Calibration)**: Inability of models to accurately assess their own parametric knowledge boundaries before triggering unnecessary retrieval.

- **Challenge 4 (Context Window Overhead and Reranking Latency)**: High computational latency of cross-encoder rerankers in high-throughput streaming systems.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
