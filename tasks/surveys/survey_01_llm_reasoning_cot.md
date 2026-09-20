---
id: survey_01_llm_reasoning_cot
type: survey
field: llm_and_reasoning
title: "Towards Reasoning in Large Language Models: A Survey"
arxiv_id: "2212.09597"
authors: "Jie Huang, Kevin Chen-Chuan Chang"
source_url: "https://arxiv.org/abs/2212.09597"
pdf_url: "https://arxiv.org/pdf/2212.09597.pdf"
keywords:
  - complex-reasoning
  - chain-of-thought
  - prompt-reasoning
  - process-verification
  - reasoning-bounds
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---

# Towards Reasoning in Large Language Models: A Survey

## 1. Verified Paper Identity & Links
- **Title**: Towards Reasoning in Large Language Models: A Survey
- **Authors**: Jie Huang, Kevin Chen-Chuan Chang
- **arXiv Entry**: [https://arxiv.org/abs/2212.09597](https://arxiv.org/abs/2212.09597)
- **Full PDF**: [https://arxiv.org/pdf/2212.09597.pdf](https://arxiv.org/pdf/2212.09597.pdf)
- **Field**: llm_and_reasoning

## 2. Official Paper Abstract
Reasoning, as an essential ability for complex problem-solving, can provide back-end support for various real-world applications, such as medical diagnosis, negotiation, etc. This paper provides a comprehensive survey of cutting-edge research on reasoning with language model prompting. We introduce research works with comparisons and summaries and provide systematic resources to help beginners. We also discuss the potential reasons for emerging such reasoning abilities and highlight future research directions. Resources are available at <a href="https://github.com/zjunlp/Prompt4ReasoningPapers" rel="external noopener nofollow" class="link-external link-https">this https URL</a> (updated periodically).

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Spurious Reasoning Paths & Unfaithful Rationales)**: Generated reasoning steps often deviate from internal computations, producing correct final answers through flawed intermediate logical steps.

- **Challenge 2 (Catastrophic Error Accumulation in Multi-Step Chains)**: In long deductive chains (>10 steps), the probability of generating at least one faulty deduction approaches 1.0 without step-level verification.

- **Challenge 3 (Inherent Limits of Autoregressive Search without Backtracking)**: Standard next-token generation cannot backtrack when entering dead ends during complex proof searches.

- **Challenge 4 (Generalization to Out-of-Distribution Problem Geometries)**: CoT methods fail when problem premises are perturbed or framed with counter-intuitive symbolic variables.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
