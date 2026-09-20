---
id: survey_09_llm_continual_learning
type: survey
field: adaptation_and_continual
title: "A Comprehensive Survey of Continual Learning in the Era of Large Language Models"
arxiv_id: "2401.16386"
authors: "Liyuan Wang et al."
source_url: "https://arxiv.org/abs/2401.16386"
pdf_url: "https://arxiv.org/pdf/2401.16386.pdf"
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

# A Comprehensive Survey of Continual Learning in the Era of Large Language Models

## 1. Verified Paper Identity & Links
- **Title**: A Comprehensive Survey of Continual Learning in the Era of Large Language Models
- **Authors**: Liyuan Wang et al.
- **arXiv Entry**: [https://arxiv.org/abs/2401.16386](https://arxiv.org/abs/2401.16386)
- **Full PDF**: [https://arxiv.org/pdf/2401.16386.pdf](https://arxiv.org/pdf/2401.16386.pdf)
- **Field**: adaptation_and_continual

## 2. Official Paper Abstract
Nowadays, real-world applications often face streaming data, which requires the learning system to absorb new knowledge as data evolves. Continual Learning (CL) aims to achieve this goal and meanwhile overcome the catastrophic forgetting of former knowledge when learning new ones. Typical CL methods build the model from scratch to grow with incoming data. However, the advent of the pre-trained model (PTM) era has sparked immense research interest, particularly in leveraging PTMs&#39; robust representational capabilities. This paper presents a comprehensive survey of the latest advancements in PTM-based CL. We categorize existing methodologies into three distinct groups, providing a comparative analysis of their similarities, differences, and respective advantages and disadvantages. Additionally, we offer an empirical study contrasting various state-of-the-art methods to highlight concerns regarding fairness in comparisons. The source code to reproduce these evaluations is available at: <a href="https://github.com/sun-hailong/LAMDA-PILOT" rel="external noopener nofollow" class="link-external link-https">this https URL</a>

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Plasticity-Stability Trade-Off in Scale)**: Sequentially fine-tuning foundation models on new domains progressively degrades general reasoning and coding skills.

- **Challenge 2 (Internal Parametric Knowledge Conflict)**: Updating outdated facts creates cognitive dissonance where models output contradictory answers across rephrased prompts.

- **Challenge 3 (Combinatorial Explosion in Dynamic Modular Expansion)**: Managing and routing across hundreds of task-specific parameter adapters without latency degradation.

- **Challenge 4 (Safety and Alignment Degradation)**: Continual domain pretraining frequently overrides prior safety alignment, reopening patched vulnerabilities.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
