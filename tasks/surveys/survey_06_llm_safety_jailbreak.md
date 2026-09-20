---
id: survey_06_llm_safety_jailbreak
type: survey
field: trustworthy_and_safety
title: "A Survey on Recent Advances in Jailbreak Attacks and Defenses of Large Language Models"
arxiv_id: "2407.04295"
authors: "Sheng Yi et al."
source_url: "https://arxiv.org/abs/2407.04295"
pdf_url: "https://arxiv.org/pdf/2407.04295.pdf"
keywords:
  - jailbreak-attacks
  - safety-alignment
  - adversarial-prompts
  - refusal-mechanisms
  - over-refusal
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---

# A Survey on Recent Advances in Jailbreak Attacks and Defenses of Large Language Models

## 1. Verified Paper Identity & Links
- **Title**: A Survey on Recent Advances in Jailbreak Attacks and Defenses of Large Language Models
- **Authors**: Sheng Yi et al.
- **arXiv Entry**: [https://arxiv.org/abs/2407.04295](https://arxiv.org/abs/2407.04295)
- **Full PDF**: [https://arxiv.org/pdf/2407.04295.pdf](https://arxiv.org/pdf/2407.04295.pdf)
- **Field**: trustworthy_and_safety

## 2. Official Paper Abstract
Large Language Models (LLMs) have performed exceptionally in various text-generative tasks, including question answering, translation, code completion, etc. However, the over-assistance of LLMs has raised the challenge of &#34;jailbreaking&#34;, which induces the model to generate malicious responses against the usage policy and society by designing adversarial prompts. With the emergence of jailbreak attack methods exploiting different vulnerabilities in LLMs, the corresponding safety alignment measures are also evolving. In this paper, we propose a comprehensive and detailed taxonomy of jailbreak attack and defense methods. For instance, the attack methods are divided into black-box and white-box attacks based on the transparency of the target model. Meanwhile, we classify defense methods into prompt-level and model-level defenses. Additionally, we further subdivide these attack and defense methods into distinct sub-classes and present a coherent diagram illustrating their relationships. We also conduct an investigation into the current evaluation methods and compare them from different perspectives. Our findings aim to inspire future research and practical implementations in safeguarding LLMs against adversarial attacks. Above all, although jailbreak remains a significant concern within the community, we believe that our work enhances the understanding of this domain and provides a foundation for developing more secure LLMs.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Catastrophic Over-Refusal / Censorship)**: Strict safety alignment triggers false refusals on benign historical, educational, or cybersecurity research queries.

- **Challenge 2 (Transferable Adversarial Token Suffixes)**: Automated optimization discovers universal token perturbations that bypass guardrails across diverse model families.

- **Challenge 3 (Surface-Level Refusal vs Internal Safety)**: Safety tuning primarily suppresses target output tokens while internal concept representations remain easily steerable.

- **Challenge 4 (Multilingual and Low-Resource Safety Vulnerabilities)**: Significant drops in refusal rates when malicious prompts are translated into low-resource languages or cipher encodings.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
