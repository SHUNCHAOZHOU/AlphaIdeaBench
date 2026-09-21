---
id: survey_09_llm_continual_learning
type: survey
field: adaptation_and_continual
title: "Continual Learning of Large Language Models: A Comprehensive Survey"
arxiv_id: "2404.16789"
authors: "Haizhou Shi, Zihao Xu, Hengyi Wang et al."
source_url: "https://arxiv.org/abs/2404.16789"
pdf_url: "https://arxiv.org/pdf/2404.16789.pdf"
keywords:
  - continual-learning
  - catastrophic-forgetting
  - knowledge-updating
  - parameter-expansion
  - plasticity-loss
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---
# Continual Learning of Large Language Models: A Comprehensive Survey

## 1. Verified Paper Identity & Links
- **Title**: Continual Learning of Large Language Models: A Comprehensive Survey
- **Authors**: Haizhou Shi, Zihao Xu, Hengyi Wang et al.
- **arXiv Entry**: [https://arxiv.org/abs/2404.16789](https://arxiv.org/abs/2404.16789)
- **Full PDF**: [https://arxiv.org/pdf/2404.16789.pdf](https://arxiv.org/pdf/2404.16789.pdf)
- **Field**: adaptation_and_continual

## 2. Official Paper Abstract
The recent success of large language models (LLMs) trained on static, pre-collected, general datasets has sparked numerous research directions and applications. One such direction addresses the non-trivial challenge of integrating pre-trained LLMs into dynamic data distributions, task structures, and user preferences. Pre-trained LLMs, when tailored for specific needs, often experience significant performance degradation in previous knowledge domains -- a phenomenon known as "catastrophic forgetting". While extensively studied in the continual learning (CL) community, it presents new manifestations in the realm of LLMs. In this survey, we provide a comprehensive overview of the current research progress on LLMs within the context of CL. This survey is structured into four main sections: we first describe an overview of continually learning LLMs, consisting of two directions of continuity: vertical continuity (or vertical continual learning), i.e., continual adaptation from general to specific capabilities, and horizontal continuity (or horizontal continual learning), i.e., continual adaptation across time and domains (Section 3). We then summarize three stages of learning LLMs in the context of modern CL: Continual Pre-Training (CPT), Domain-Adaptive Pre-training (DAP), and Continual Fine-Tuning (CFT) (Section 4). Then we provide an overview of evaluation protocols for continual learning with LLMs, along with the current available data sources (Section 5). Finally, we discuss intriguing questions pertaining to continual learning for LLMs (Section 6). The full list of papers examined in this survey is available at https://github.com/Wang-ML-Lab/llm-continual-learning-survey.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Plasticity-Stability Trade-Off in Scale)**: Sequentially fine-tuning foundation models on new domains progressively degrades general reasoning and coding skills.

- **Challenge 2 (Internal Parametric Knowledge Conflict)**: Updating outdated facts creates cognitive dissonance where models output contradictory answers across rephrased prompts.

- **Challenge 3 (Combinatorial Explosion in Dynamic Modular Expansion)**: Managing and routing across hundreds of task-specific parameter adapters without latency degradation.

- **Challenge 4 (Safety and Alignment Degradation)**: Continual domain pretraining frequently overrides prior safety alignment, reopening patched vulnerabilities.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
