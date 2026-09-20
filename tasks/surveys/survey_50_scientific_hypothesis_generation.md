---
id: survey_50_scientific_hypothesis_generation
type: survey
field: ai_for_science
title: "Scientific Discovery in the Age of Artificial Intelligence"
arxiv_id: "2304.12210"
authors: "Wang et al."
source_url: "https://arxiv.org/abs/2304.12210"
pdf_url: "https://arxiv.org/pdf/2304.12210.pdf"
keywords:
  - scientific-discovery
  - hypothesis-generation
  - automated-science
  - literature-mining
  - closed-loop-labs
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---

# Scientific Discovery in the Age of Artificial Intelligence

## 1. Verified Paper Identity & Links
- **Title**: Scientific Discovery in the Age of Artificial Intelligence
- **Authors**: Wang et al.
- **arXiv Entry**: [https://arxiv.org/abs/2304.12210](https://arxiv.org/abs/2304.12210)
- **Full PDF**: [https://arxiv.org/pdf/2304.12210.pdf](https://arxiv.org/pdf/2304.12210.pdf)
- **Field**: ai_for_science

## 2. Official Paper Abstract
Self-supervised learning, dubbed the dark matter of intelligence, is a promising path to advance machine learning. Yet, much like cooking, training SSL methods is a delicate art with a high barrier to entry. While many components are familiar, successfully training a SSL method involves a dizzying set of choices from the pretext tasks to training hyper-parameters. Our goal is to lower the barrier to entry into SSL research by laying the foundations and latest SSL recipes in the style of a cookbook. We hope to empower the curious researcher to navigate the terrain of methods, understand the role of the various knobs, and gain the know-how required to explore how delicious SSL can be.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Scalability Bottlenecks in scientific-discovery)**: Computational and memory ceilings when scaling algorithms on high-dimensional inputs.

- **Challenge 2 (Generalization & Distribution Shifts in hypothesis-generation)**: Performance degradation when evaluated on out-of-distribution benchmarks and dynamic environments.

- **Challenge 3 (Evaluation Gaps & Alignment with automated-science)**: Disconnect between current proxy metrics and authentic downstream utility.

- **Challenge 4 (Theoretical Foundations of literature-mining)**: Establishing formal guarantees and provable bounds on convergence and stability.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
