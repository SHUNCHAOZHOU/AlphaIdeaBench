---
id: survey_34_mathematical_automated_proving
type: survey
field: llm_and_reasoning
title: "A Survey on Deep Learning for Theorem Proving"
arxiv_id: "2404.09939"
authors: "Zhaoyu Li, Jialiang Sun, Logan Murphy et al."
source_url: "https://arxiv.org/abs/2404.09939"
pdf_url: "https://arxiv.org/pdf/2404.09939.pdf"
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
- **Authors**: Zhaoyu Li, Jialiang Sun, Logan Murphy et al.
- **arXiv Entry**: [https://arxiv.org/abs/2404.09939](https://arxiv.org/abs/2404.09939)
- **Full PDF**: [https://arxiv.org/pdf/2404.09939.pdf](https://arxiv.org/pdf/2404.09939.pdf)
- **Field**: llm_and_reasoning

## 2. Official Paper Abstract
Theorem proving is a fundamental aspect of mathematics, spanning from informal reasoning in natural language to rigorous derivations in formal systems. In recent years, the advancement of deep learning, especially the emergence of large language models, has sparked a notable surge of research exploring these techniques to enhance the process of theorem proving. This paper presents a comprehensive survey of deep learning for theorem proving by offering (i) a thorough review of existing approaches across various tasks such as autoformalization, premise selection, proofstep generation, and proof search; (ii) an extensive summary of curated datasets and strategies for synthetic data generation; (iii) a detailed analysis of evaluation metrics and the performance of state-of-the-art methods; and (iv) a critical discussion on the persistent challenges and the promising avenues for future exploration. Our survey aims to serve as a foundational reference for deep learning approaches in theorem proving, inspiring and catalyzing further research endeavors in this rapidly growing field. A curated list of papers is available at https://github.com/zhaoyu-li/DL4TP.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Scalability Bottlenecks in automated-theorem-proving)**: Computational and memory ceilings when scaling algorithms on high-dimensional inputs.

- **Challenge 2 (Generalization & Distribution Shifts in formal-mathematics)**: Performance degradation when evaluated on out-of-distribution benchmarks and dynamic environments.

- **Challenge 3 (Evaluation Gaps & Alignment with lean4)**: Disconnect between current proxy metrics and authentic downstream utility.

- **Challenge 4 (Theoretical Foundations of isabelle)**: Establishing formal guarantees and provable bounds on convergence and stability.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
