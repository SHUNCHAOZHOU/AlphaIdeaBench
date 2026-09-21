---
id: survey_39_reward_modeling_hacking
type: survey
field: trustworthy_and_safety
title: "RewardBench: Evaluating Reward Models for Language Modeling"
arxiv_id: "2403.13787"
authors: "Nathan Lambert, Valentina Pyatkin, Jacob Morrison et al."
source_url: "https://arxiv.org/abs/2403.13787"
pdf_url: "https://arxiv.org/pdf/2403.13787.pdf"
keywords:
  - reward-modeling
  - reward-hacking
  - goodharts-law
  - preference-learning
  - process-rewards
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---
# RewardBench: Evaluating Reward Models for Language Modeling

## 1. Verified Paper Identity & Links
- **Title**: RewardBench: Evaluating Reward Models for Language Modeling
- **Authors**: Nathan Lambert, Valentina Pyatkin, Jacob Morrison et al.
- **arXiv Entry**: [https://arxiv.org/abs/2403.13787](https://arxiv.org/abs/2403.13787)
- **Full PDF**: [https://arxiv.org/pdf/2403.13787.pdf](https://arxiv.org/pdf/2403.13787.pdf)
- **Field**: trustworthy_and_safety

## 2. Official Paper Abstract
Reward models (RMs) are at the crux of successfully using RLHF to align pretrained models to human preferences, yet there has been relatively little study that focuses on evaluation of those models. Evaluating reward models presents an opportunity to understand the opaque technologies used for alignment of language models and which values are embedded in them. Resources for reward model training and understanding are sparse in the nascent open-source community around them. To enhance scientific understanding of reward models, we present RewardBench, a benchmark dataset and code-base for evaluation. The RewardBench dataset is a collection of prompt-chosen-rejected trios spanning chat, reasoning, and safety, to benchmark how reward models perform on challenging, structured and out-of-distribution queries. We create specific comparison datasets for RMs that have subtle, but verifiable reasons (e.g. bugs, incorrect facts) why one answer should be preferred to another. On the RewardBench leaderboard, we evaluate reward models trained with a variety of methods, such as the direct MLE training of classifiers and the implicit reward modeling of Direct Preference Optimization (DPO). We present many findings on propensity for refusals, reasoning limitations, and instruction following shortcomings of various reward models towards a better understanding of the RLHF process.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Scalability Bottlenecks in reward-modeling)**: Computational and memory ceilings when scaling algorithms on high-dimensional inputs.

- **Challenge 2 (Generalization & Distribution Shifts in reward-hacking)**: Performance degradation when evaluated on out-of-distribution benchmarks and dynamic environments.

- **Challenge 3 (Evaluation Gaps & Alignment with goodharts-law)**: Disconnect between current proxy metrics and authentic downstream utility.

- **Challenge 4 (Theoretical Foundations of preference-learning)**: Establishing formal guarantees and provable bounds on convergence and stability.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
