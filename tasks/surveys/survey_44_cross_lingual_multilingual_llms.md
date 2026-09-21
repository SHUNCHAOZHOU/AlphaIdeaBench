---
id: survey_44_cross_lingual_multilingual_llms
type: survey
field: llm_and_reasoning
title: "A Survey on Multilingual Large Language Models: Corpora, Alignment, and Bias"
arxiv_id: "2404.00929"
authors: "Yuemei Xu, Ling Hu, Jiayi Zhao et al."
source_url: "https://arxiv.org/abs/2404.00929"
pdf_url: "https://arxiv.org/pdf/2404.00929.pdf"
keywords:
  - multilingual-llm
  - low-resource-languages
  - cross-lingual-transfer
  - tokenization-fertility
  - cultural-alignment
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---
# A Survey on Multilingual Large Language Models: Corpora, Alignment, and Bias

## 1. Verified Paper Identity & Links
- **Title**: A Survey on Multilingual Large Language Models: Corpora, Alignment, and Bias
- **Authors**: Yuemei Xu, Ling Hu, Jiayi Zhao et al.
- **arXiv Entry**: [https://arxiv.org/abs/2404.00929](https://arxiv.org/abs/2404.00929)
- **Full PDF**: [https://arxiv.org/pdf/2404.00929.pdf](https://arxiv.org/pdf/2404.00929.pdf)
- **Field**: llm_and_reasoning

## 2. Official Paper Abstract
Based on the foundation of Large Language Models (LLMs), Multilingual LLMs (MLLMs) have been developed to address the challenges faced in multilingual natural language processing, hoping to achieve knowledge transfer from high-resource languages to low-resource languages. However, significant limitations and challenges still exist, such as language imbalance, multilingual alignment, and inherent bias. In this paper, we aim to provide a comprehensive analysis of MLLMs, delving deeply into discussions surrounding these critical issues. First of all, we start by presenting an overview of MLLMs, covering their evolutions, key techniques, and multilingual capacities. Secondly, we explore the multilingual training corpora of MLLMs and the multilingual datasets oriented for downstream tasks that are crucial to enhance the cross-lingual capability of MLLMs. Thirdly, we survey the state-of-the-art studies of multilingual representations and investigate whether the current MLLMs can learn a universal language representation. Fourthly, we discuss bias on MLLMs, including its categories, evaluation metrics, and debiasing techniques. Finally, we discuss existing challenges and point out promising research directions of MLLMs.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Scalability Bottlenecks in multilingual-llm)**: Computational and memory ceilings when scaling algorithms on high-dimensional inputs.

- **Challenge 2 (Generalization & Distribution Shifts in low-resource-languages)**: Performance degradation when evaluated on out-of-distribution benchmarks and dynamic environments.

- **Challenge 3 (Evaluation Gaps & Alignment with cross-lingual-transfer)**: Disconnect between current proxy metrics and authentic downstream utility.

- **Challenge 4 (Theoretical Foundations of tokenization-fertility)**: Establishing formal guarantees and provable bounds on convergence and stability.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
