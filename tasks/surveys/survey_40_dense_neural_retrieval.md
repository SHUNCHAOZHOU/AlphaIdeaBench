---
id: survey_40_dense_neural_retrieval
type: survey
field: llm_and_reasoning
title: "Large Language Models for Information Retrieval: A Survey"
arxiv_id: "2308.07107"
authors: "Yutao Zhu, Huaying Yuan, Shuting Wang et al."
source_url: "https://arxiv.org/abs/2308.07107"
pdf_url: "https://arxiv.org/pdf/2308.07107.pdf"
keywords:
  - neural-information-retrieval
  - dense-retrieval
  - colbert
  - hard-negative-mining
  - vector-search
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---
# Large Language Models for Information Retrieval: A Survey

## 1. Verified Paper Identity & Links
- **Title**: Large Language Models for Information Retrieval: A Survey
- **Authors**: Yutao Zhu, Huaying Yuan, Shuting Wang et al.
- **arXiv Entry**: [https://arxiv.org/abs/2308.07107](https://arxiv.org/abs/2308.07107)
- **Full PDF**: [https://arxiv.org/pdf/2308.07107.pdf](https://arxiv.org/pdf/2308.07107.pdf)
- **Field**: llm_and_reasoning

## 2. Official Paper Abstract
As a primary means of information acquisition, information retrieval (IR) systems, such as search engines, have integrated themselves into our daily lives. These systems also serve as components of dialogue, question-answering, and recommender systems. The trajectory of IR has evolved dynamically from its origins in term-based methods to its integration with advanced neural models. While the neural models excel at capturing complex contextual signals and semantic nuances, thereby reshaping the IR landscape, they still face challenges such as data scarcity, interpretability, and the generation of contextually plausible yet potentially inaccurate responses. This evolution requires a combination of both traditional methods (such as term-based sparse retrieval methods with rapid response) and modern neural architectures (such as language models with powerful language understanding capacity). Meanwhile, the emergence of large language models (LLMs), typified by ChatGPT and GPT-4, has revolutionized natural language processing due to their remarkable language understanding, generation, generalization, and reasoning abilities. Consequently, recent research has sought to leverage LLMs to improve IR systems. Given the rapid evolution of this research trajectory, it is necessary to consolidate existing methodologies and provide nuanced insights through a comprehensive overview. In this survey, we delve into the confluence of LLMs and IR systems, including crucial aspects such as query rewriters, retrievers, rerankers, and readers. Additionally, we explore promising directions, such as search agents, within this expanding field.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Scalability Bottlenecks in neural-information-retrieval)**: Computational and memory ceilings when scaling algorithms on high-dimensional inputs.

- **Challenge 2 (Generalization & Distribution Shifts in dense-retrieval)**: Performance degradation when evaluated on out-of-distribution benchmarks and dynamic environments.

- **Challenge 3 (Evaluation Gaps & Alignment with colbert)**: Disconnect between current proxy metrics and authentic downstream utility.

- **Challenge 4 (Theoretical Foundations of hard-negative-mining)**: Establishing formal guarantees and provable bounds on convergence and stability.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
