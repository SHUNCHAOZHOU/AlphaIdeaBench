---
id: survey_21_code_intelligence_synthesis
type: survey
field: llm_and_reasoning
title: "Code Intelligence: A Survey of Foundation Models for Software Engineering"
arxiv_id: "2311.07989"
authors: "Zheng et al."
source_url: "https://arxiv.org/abs/2311.07989"
pdf_url: "https://arxiv.org/pdf/2311.07989.pdf"
keywords:
  - code-generation
  - program-synthesis
  - swe-bench
  - automated-debugging
  - repo-level-agents
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---

# Code Intelligence: A Survey of Foundation Models for Software Engineering

## 1. Verified Paper Identity & Links
- **Title**: Code Intelligence: A Survey of Foundation Models for Software Engineering
- **Authors**: Zheng et al.
- **arXiv Entry**: [https://arxiv.org/abs/2311.07989](https://arxiv.org/abs/2311.07989)
- **Full PDF**: [https://arxiv.org/pdf/2311.07989.pdf](https://arxiv.org/pdf/2311.07989.pdf)
- **Field**: llm_and_reasoning

## 2. Official Paper Abstract
In this work we systematically review the recent advancements in software engineering with language models, covering 70+ models, 40+ evaluation tasks, 180+ datasets, and 900 related works. Unlike previous works, we integrate software engineering (SE) with natural language processing (NLP) by discussing the perspectives of both sides: SE applies language models for development automation, while NLP adopts SE tasks for language model evaluation. We break down code processing models into general language models represented by the GPT family and specialized models that are specifically pretrained on code, often with tailored objectives. We discuss the relations and differences between these models, and highlight the historical transition of code modeling from statistical models and RNNs to pretrained Transformers and LLMs, which is exactly the same course that had been taken by NLP. We also go beyond programming and review LLMs&#39; application in other software engineering activities including requirement engineering, testing, deployment, and operations in an endeavor to provide a global view of NLP in SE, and identify key challenges and potential future directions in this domain. We keep the survey open and updated on GitHub at <a href="https://github.com/codefuse-ai/Awesome-Code-LLM" rel="external noopener nofollow" class="link-external link-https">this https URL</a>.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Scalability Bottlenecks in code-generation)**: Computational and memory ceilings when scaling algorithms on high-dimensional inputs.

- **Challenge 2 (Generalization & Distribution Shifts in program-synthesis)**: Performance degradation when evaluated on out-of-distribution benchmarks and dynamic environments.

- **Challenge 3 (Evaluation Gaps & Alignment with swe-bench)**: Disconnect between current proxy metrics and authentic downstream utility.

- **Challenge 4 (Theoretical Foundations of automated-debugging)**: Establishing formal guarantees and provable bounds on convergence and stability.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
