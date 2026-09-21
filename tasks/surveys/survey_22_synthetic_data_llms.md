---
id: survey_22_synthetic_data_llms
type: survey
field: llm_and_reasoning
title: "Best Practices and Lessons Learned on Synthetic Data"
arxiv_id: "2404.07503"
authors: "Ruibo Liu, Jerry Wei, Fangyu Liu et al."
source_url: "https://arxiv.org/abs/2404.07503"
pdf_url: "https://arxiv.org/pdf/2404.07503.pdf"
keywords:
  - synthetic-data
  - data-curation
  - model-collapse
  - benchmark-contamination
  - quality-filtering
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---
# Best Practices and Lessons Learned on Synthetic Data

## 1. Verified Paper Identity & Links
- **Title**: Best Practices and Lessons Learned on Synthetic Data
- **Authors**: Ruibo Liu, Jerry Wei, Fangyu Liu et al.
- **arXiv Entry**: [https://arxiv.org/abs/2404.07503](https://arxiv.org/abs/2404.07503)
- **Full PDF**: [https://arxiv.org/pdf/2404.07503.pdf](https://arxiv.org/pdf/2404.07503.pdf)
- **Field**: llm_and_reasoning

## 2. Official Paper Abstract
The success of AI models relies on the availability of large, diverse, and high-quality datasets, which can be challenging to obtain due to data scarcity, privacy concerns, and high costs. Synthetic data has emerged as a promising solution by generating artificial data that mimics real-world patterns. This paper provides an overview of synthetic data research, discussing its applications, challenges, and future directions. We present empirical evidence from prior art to demonstrate its effectiveness and highlight the importance of ensuring its factuality, fidelity, and unbiasedness. We emphasize the need for responsible use of synthetic data to build more powerful, inclusive, and trustworthy language models.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Scalability Bottlenecks in synthetic-data)**: Computational and memory ceilings when scaling algorithms on high-dimensional inputs.

- **Challenge 2 (Generalization & Distribution Shifts in data-curation)**: Performance degradation when evaluated on out-of-distribution benchmarks and dynamic environments.

- **Challenge 3 (Evaluation Gaps & Alignment with model-collapse)**: Disconnect between current proxy metrics and authentic downstream utility.

- **Challenge 4 (Theoretical Foundations of benchmark-contamination)**: Establishing formal guarantees and provable bounds on convergence and stability.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
