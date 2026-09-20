---
id: survey_16_long_context_llms
type: survey
field: llm_and_reasoning
title: "A Survey on Long Context Large Language Models"
arxiv_id: "2403.11602"
authors: "Dawei Zhu et al."
source_url: "https://arxiv.org/abs/2403.11602"
pdf_url: "https://arxiv.org/pdf/2403.11602.pdf"
keywords:
  - long-context-llm
  - rope-interpolation
  - context-extension
  - lost-in-the-middle
  - needle-in-a-haystack
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---

# A Survey on Long Context Large Language Models

## 1. Verified Paper Identity & Links
- **Title**: A Survey on Long Context Large Language Models
- **Authors**: Dawei Zhu et al.
- **arXiv Entry**: [https://arxiv.org/abs/2403.11602](https://arxiv.org/abs/2403.11602)
- **Full PDF**: [https://arxiv.org/pdf/2403.11602.pdf](https://arxiv.org/pdf/2403.11602.pdf)
- **Field**: llm_and_reasoning

## 2. Official Paper Abstract
In this manuscript we present how to collapse a manifold equipped with a closed flat regular Riemannian foliation with leaves of positive dimension, while keeping the sectional curvature uniformly bounded from above and below. From this deformation, we show that in the case when the manifold is compact and simply connected the foliation is given by torus actions. This gives a geometric characterization of aspherical regular Riemannian foliations given by torus actions

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Multi-Needle Reasoning and Synthesis)**: Models pass single-needle retrieval easily but fail when required to synthesize evidence scattered across 10+ passages.

- **Challenge 2 (Attention Dilution & Lost-in-the-Middle)**: Information located in the middle 20%-80% of context windows receives systematically lower attention weights.

- **Challenge 3 (Quadratic Computational Cost of Full Attention)**: Real-time processing of 1M+ token sequences is intractable without severe KV cache compression.

- **Challenge 4 (Scarcity of Genuine Long-Document Training Data)**: Pretraining corpora contain few authentically coherent 500k+ token long documents.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
