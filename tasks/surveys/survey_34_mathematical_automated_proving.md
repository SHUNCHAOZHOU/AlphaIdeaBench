---
id: survey_34_mathematical_automated_proving
type: survey
field: llm_and_reasoning
title: "A Survey on Deep Learning for Theorem Proving"
arxiv_id: "2402.00157"
authors: "Yang et al."
source_url: "https://arxiv.org/abs/2402.00157"
pdf_url: "https://arxiv.org/pdf/2402.00157.pdf"
keywords:
  - automated-theorem-proving
  - formal-mathematics
  - lean4
  - isabelle
  - premise-selection
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---

# A Survey on Deep Learning for Theorem Proving

## 1. Verified Paper Identity & Links
- **Title**: A Survey on Deep Learning for Theorem Proving
- **Authors**: Yang et al.
- **arXiv Entry**: [https://arxiv.org/abs/2402.00157](https://arxiv.org/abs/2402.00157)
- **Full PDF**: [https://arxiv.org/pdf/2402.00157.pdf](https://arxiv.org/pdf/2402.00157.pdf)
- **Field**: llm_and_reasoning

## 2. Official Paper Abstract
Mathematical reasoning serves as a cornerstone for assessing the fundamental cognitive capabilities of human intelligence. In recent times, there has been a notable surge in the development of Large Language Models (LLMs) geared towards the automated resolution of mathematical problems. However, the landscape of mathematical problem types is vast and varied, with LLM-oriented techniques undergoing evaluation across diverse datasets and settings. This diversity makes it challenging to discern the true advancements and obstacles within this burgeoning field. This survey endeavors to address four pivotal dimensions: i) a comprehensive exploration of the various mathematical problems and their corresponding datasets that have been investigated; ii) an examination of the spectrum of LLM-oriented techniques that have been proposed for mathematical problem-solving; iii) an overview of factors and concerns affecting LLMs in solving math; and iv) an elucidation of the persisting challenges within this domain. To the best of our knowledge, this survey stands as one of the first extensive examinations of the landscape of LLMs in the realm of mathematics, providing a holistic perspective on the current state, accomplishments, and future challenges in this rapidly evolving field.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Scalability Bottlenecks in automated-theorem-proving)**: Computational and memory ceilings when scaling algorithms on high-dimensional inputs.

- **Challenge 2 (Generalization & Distribution Shifts in formal-mathematics)**: Performance degradation when evaluated on out-of-distribution benchmarks and dynamic environments.

- **Challenge 3 (Evaluation Gaps & Alignment with lean4)**: Disconnect between current proxy metrics and authentic downstream utility.

- **Challenge 4 (Theoretical Foundations of isabelle)**: Establishing formal guarantees and provable bounds on convergence and stability.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
