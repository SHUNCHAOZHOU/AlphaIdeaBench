---
id: survey_04_llm_agent_collaboration
type: survey
field: llm_and_reasoning
title: "A Survey on Large Language Model based Autonomous Agents"
arxiv_id: "2308.11432"
authors: "Lei Wang, Chen Ma, Xueyang Feng et al."
source_url: "https://arxiv.org/abs/2308.11432"
pdf_url: "https://arxiv.org/pdf/2308.11432.pdf"
keywords:
  - autonomous-agents
  - multi-agent-collaboration
  - agentic-planning
  - tool-execution
  - long-horizon-memory
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---

# A Survey on Large Language Model based Autonomous Agents

## 1. Verified Paper Identity & Links
- **Title**: A Survey on Large Language Model based Autonomous Agents
- **Authors**: Lei Wang, Chen Ma, Xueyang Feng et al.
- **arXiv Entry**: [https://arxiv.org/abs/2308.11432](https://arxiv.org/abs/2308.11432)
- **Full PDF**: [https://arxiv.org/pdf/2308.11432.pdf](https://arxiv.org/pdf/2308.11432.pdf)
- **Field**: llm_and_reasoning

## 2. Official Paper Abstract
Autonomous agents have long been a prominent research focus in both academic and industry communities. Previous research in this field often focuses on training agents with limited knowledge within isolated environments, which diverges significantly from human learning processes, and thus makes the agents hard to achieve human-like decisions. Recently, through the acquisition of vast amounts of web knowledge, large language models (LLMs) have demonstrated remarkable potential in achieving human-level intelligence. This has sparked an upsurge in studies investigating LLM-based autonomous agents. In this paper, we present a comprehensive survey of these studies, delivering a systematic review of the field of LLM-based autonomous agents from a holistic perspective. More specifically, we first discuss the construction of LLM-based autonomous agents, for which we propose a unified framework that encompasses a majority of the previous work. Then, we present a comprehensive overview of the diverse applications of LLM-based autonomous agents in the fields of social science, natural science, and engineering. Finally, we delve into the evaluation strategies commonly used for LLM-based autonomous agents. Based on the previous studies, we also present several challenges and future directions in this field. To keep track of this field and continuously update our survey, we maintain a repository of relevant references at <a href="https://github.com/Paitesanshi/LLM-Agent-Survey" rel="external noopener nofollow" class="link-external link-https">this https URL</a>.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Long-Horizon Error Compounding)**: Early execution mistakes in multi-step task workflows rapidly propagate, resulting in irreversible downstream task failure.

- **Challenge 2 (Multi-Agent Sycophancy & Hallucinatory Consensus)**: Collaborative agents frequently reinforce each other's hallucinations rather than providing rigorous critique.

- **Challenge 3 (Episodic Memory Retrieval Degradation)**: Vector databases retrieve out-of-context historical fragments lacking hierarchical structure and temporal invalidation.

- **Challenge 4 (Environment Feedback Grounding)**: Parsing unstructured terminal outputs, compiler errors, or multimodal environmental observations into valid recovery actions.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
