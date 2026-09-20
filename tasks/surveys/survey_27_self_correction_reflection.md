---
id: survey_27_self_correction_reflection
type: survey
field: llm_and_reasoning
title: "Large Language Models Cannot Self-Correct Reasoning Yet"
arxiv_id: "2310.01798"
authors: "Huang et al."
source_url: "https://arxiv.org/abs/2310.01798"
pdf_url: "https://arxiv.org/pdf/2310.01798.pdf"
keywords:
  - self-correction
  - intrinsic-reflection
  - hallucination-correction
  - external-feedback
  - overconfidence
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---

# Large Language Models Cannot Self-Correct Reasoning Yet

## 1. Verified Paper Identity & Links
- **Title**: Large Language Models Cannot Self-Correct Reasoning Yet
- **Authors**: Huang et al.
- **arXiv Entry**: [https://arxiv.org/abs/2310.01798](https://arxiv.org/abs/2310.01798)
- **Full PDF**: [https://arxiv.org/pdf/2310.01798.pdf](https://arxiv.org/pdf/2310.01798.pdf)
- **Field**: llm_and_reasoning

## 2. Official Paper Abstract
Large Language Models (LLMs) have emerged as a groundbreaking technology with their unparalleled text generation capabilities across various applications. Nevertheless, concerns persist regarding the accuracy and appropriateness of their generated content. A contemporary methodology, self-correction, has been proposed as a remedy to these issues. Building upon this premise, this paper critically examines the role and efficacy of self-correction within LLMs, shedding light on its true potential and limitations. Central to our investigation is the notion of intrinsic self-correction, whereby an LLM attempts to correct its initial responses based solely on its inherent capabilities, without the crutch of external feedback. In the context of reasoning, our research indicates that LLMs struggle to self-correct their responses without external feedback, and at times, their performance even degrades after self-correction. Drawing from these insights, we offer suggestions for future research and practical applications in this field.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Scalability Bottlenecks in self-correction)**: Computational and memory ceilings when scaling algorithms on high-dimensional inputs.

- **Challenge 2 (Generalization & Distribution Shifts in intrinsic-reflection)**: Performance degradation when evaluated on out-of-distribution benchmarks and dynamic environments.

- **Challenge 3 (Evaluation Gaps & Alignment with hallucination-correction)**: Disconnect between current proxy metrics and authentic downstream utility.

- **Challenge 4 (Theoretical Foundations of external-feedback)**: Establishing formal guarantees and provable bounds on convergence and stability.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
