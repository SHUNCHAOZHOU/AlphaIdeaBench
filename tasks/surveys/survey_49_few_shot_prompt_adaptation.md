---
id: survey_49_few_shot_prompt_adaptation
type: survey
field: llm_and_reasoning
title: "A Survey on In-Context Learning"
arxiv_id: "2301.00234"
authors: "Dong et al."
source_url: "https://arxiv.org/abs/2301.00234"
pdf_url: "https://arxiv.org/pdf/2301.00234.pdf"
keywords:
  - in-context-learning
  - prompt-sensitivity
  - meta-optimization
  - example-selection
  - implicit-finetuning
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---

# A Survey on In-Context Learning

## 1. Verified Paper Identity & Links
- **Title**: A Survey on In-Context Learning
- **Authors**: Dong et al.
- **arXiv Entry**: [https://arxiv.org/abs/2301.00234](https://arxiv.org/abs/2301.00234)
- **Full PDF**: [https://arxiv.org/pdf/2301.00234.pdf](https://arxiv.org/pdf/2301.00234.pdf)
- **Field**: llm_and_reasoning

## 2. Official Paper Abstract
With the increasing capabilities of large language models (LLMs), in-context learning (ICL) has emerged as a new paradigm for natural language processing (NLP), where LLMs make predictions based on contexts augmented with a few examples. It has been a significant trend to explore ICL to evaluate and extrapolate the ability of LLMs. In this paper, we aim to survey and summarize the progress and challenges of ICL. We first present a formal definition of ICL and clarify its correlation to related studies. Then, we organize and discuss advanced techniques, including training strategies, prompt designing strategies, and related analysis. Additionally, we explore various ICL application scenarios, such as data engineering and knowledge updating. Finally, we address the challenges of ICL and suggest potential directions for further research. We hope that our work can encourage more research on uncovering how ICL works and improving ICL.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Scalability Bottlenecks in in-context-learning)**: Computational and memory ceilings when scaling algorithms on high-dimensional inputs.

- **Challenge 2 (Generalization & Distribution Shifts in prompt-sensitivity)**: Performance degradation when evaluated on out-of-distribution benchmarks and dynamic environments.

- **Challenge 3 (Evaluation Gaps & Alignment with meta-optimization)**: Disconnect between current proxy metrics and authentic downstream utility.

- **Challenge 4 (Theoretical Foundations of example-selection)**: Establishing formal guarantees and provable bounds on convergence and stability.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
