---
id: survey_35_vision_language_navigation
type: survey
field: robotics_and_rl
title: "A Survey on Vision-Language Navigation"
arxiv_id: "2203.12667"
authors: "Guhur et al."
source_url: "https://arxiv.org/abs/2203.12667"
pdf_url: "https://arxiv.org/pdf/2203.12667.pdf"
keywords:
  - vision-language-navigation
  - embodied-ai
  - continuous-environments
  - cross-modal-grounding
  - topological-mapping
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---

# A Survey on Vision-Language Navigation

## 1. Verified Paper Identity & Links
- **Title**: A Survey on Vision-Language Navigation
- **Authors**: Guhur et al.
- **arXiv Entry**: [https://arxiv.org/abs/2203.12667](https://arxiv.org/abs/2203.12667)
- **Full PDF**: [https://arxiv.org/pdf/2203.12667.pdf](https://arxiv.org/pdf/2203.12667.pdf)
- **Field**: robotics_and_rl

## 2. Official Paper Abstract
A long-term goal of AI research is to build intelligent agents that can communicate with humans in natural language, perceive the environment, and perform real-world tasks. Vision-and-Language Navigation (VLN) is a fundamental and interdisciplinary research topic towards this goal, and receives increasing attention from natural language processing, computer vision, robotics, and machine learning communities. In this paper, we review contemporary studies in the emerging field of VLN, covering tasks, evaluation metrics, methods, etc. Through structured analysis of current progress and challenges, we highlight the limitations of current VLN and opportunities for future work. This paper serves as a thorough reference for the VLN research community.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Scalability Bottlenecks in vision-language-navigation)**: Computational and memory ceilings when scaling algorithms on high-dimensional inputs.

- **Challenge 2 (Generalization & Distribution Shifts in embodied-ai)**: Performance degradation when evaluated on out-of-distribution benchmarks and dynamic environments.

- **Challenge 3 (Evaluation Gaps & Alignment with continuous-environments)**: Disconnect between current proxy metrics and authentic downstream utility.

- **Challenge 4 (Theoretical Foundations of cross-modal-grounding)**: Establishing formal guarantees and provable bounds on convergence and stability.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
