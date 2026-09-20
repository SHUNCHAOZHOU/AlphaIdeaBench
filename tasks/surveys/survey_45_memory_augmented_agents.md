---
id: survey_45_memory_augmented_agents
type: survey
field: llm_and_reasoning
title: "MemGPT: Towards LLMs as Operating Systems"
arxiv_id: "2310.08560"
authors: "Packer et al."
source_url: "https://arxiv.org/abs/2310.08560"
pdf_url: "https://arxiv.org/pdf/2310.08560.pdf"
keywords:
  - agent-memory
  - hierarchical-memory
  - episodic-retrieval
  - working-memory
  - context-compaction
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---

# MemGPT: Towards LLMs as Operating Systems

## 1. Verified Paper Identity & Links
- **Title**: MemGPT: Towards LLMs as Operating Systems
- **Authors**: Packer et al.
- **arXiv Entry**: [https://arxiv.org/abs/2310.08560](https://arxiv.org/abs/2310.08560)
- **Full PDF**: [https://arxiv.org/pdf/2310.08560.pdf](https://arxiv.org/pdf/2310.08560.pdf)
- **Field**: llm_and_reasoning

## 2. Official Paper Abstract
Large language models (LLMs) have revolutionized AI, but are constrained by limited context windows, hindering their utility in tasks like extended conversations and document analysis. To enable using context beyond limited context windows, we propose virtual context management, a technique drawing inspiration from hierarchical memory systems in traditional operating systems that provide the appearance of large memory resources through data movement between fast and slow memory. Using this technique, we introduce MemGPT (Memory-GPT), a system that intelligently manages different memory tiers in order to effectively provide extended context within the LLM&#39;s limited context window, and utilizes interrupts to manage control flow between itself and the user. We evaluate our OS-inspired design in two domains where the limited context windows of modern LLMs severely handicaps their performance: document analysis, where MemGPT is able to analyze large documents that far exceed the underlying LLM&#39;s context window, and multi-session chat, where MemGPT can create conversational agents that remember, reflect, and evolve dynamically through long-term interactions with their users. We release MemGPT code and data for our experiments at <a href="https://memgpt.ai" rel="external noopener nofollow" class="link-external link-https">this https URL</a>.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Scalability Bottlenecks in agent-memory)**: Computational and memory ceilings when scaling algorithms on high-dimensional inputs.

- **Challenge 2 (Generalization & Distribution Shifts in hierarchical-memory)**: Performance degradation when evaluated on out-of-distribution benchmarks and dynamic environments.

- **Challenge 3 (Evaluation Gaps & Alignment with episodic-retrieval)**: Disconnect between current proxy metrics and authentic downstream utility.

- **Challenge 4 (Theoretical Foundations of working-memory)**: Establishing formal guarantees and provable bounds on convergence and stability.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
