---
id: survey_07_test_time_scaling
type: survey
field: llm_and_reasoning
title: "Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters"
arxiv_id: "2408.03314"
authors: "Charlie Snell, Jaehoon Lee, Kelvin Xu et al."
source_url: "https://arxiv.org/abs/2408.03314"
pdf_url: "https://arxiv.org/pdf/2408.03314.pdf"
keywords:
  - test-time-compute
  - inference-scaling
  - mcts
  - process-reward-models
  - budget-allocation
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---
# Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters

## 1. Verified Paper Identity & Links
- **Title**: Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters
- **Authors**: Charlie Snell, Jaehoon Lee, Kelvin Xu et al.
- **arXiv Entry**: [https://arxiv.org/abs/2408.03314](https://arxiv.org/abs/2408.03314)
- **Full PDF**: [https://arxiv.org/pdf/2408.03314.pdf](https://arxiv.org/pdf/2408.03314.pdf)
- **Field**: llm_and_reasoning

## 2. Official Paper Abstract
Enabling LLMs to improve their outputs by using more test-time computation is a critical step towards building generally self-improving agents that can operate on open-ended natural language. In this paper, we study the scaling of inference-time computation in LLMs, with a focus on answering the question: if an LLM is allowed to use a fixed but non-trivial amount of inference-time compute, how much can it improve its performance on a challenging prompt? Answering this question has implications not only on the achievable performance of LLMs, but also on the future of LLM pretraining and how one should tradeoff inference-time and pre-training compute. Despite its importance, little research attempted to understand the scaling behaviors of various test-time inference methods. Moreover, current work largely provides negative results for a number of these strategies. In this work, we analyze two primary mechanisms to scale test-time computation: (1) searching against dense, process-based verifier reward models; and (2) updating the model's distribution over a response adaptively, given the prompt at test time. We find that in both cases, the effectiveness of different approaches to scaling test-time compute critically varies depending on the difficulty of the prompt. This observation motivates applying a "compute-optimal" scaling strategy, which acts to most effectively allocate test-time compute adaptively per prompt. Using this compute-optimal strategy, we can improve the efficiency of test-time compute scaling by more than 4x compared to a best-of-N baseline. Additionally, in a FLOPs-matched evaluation, we find that on problems where a smaller base model attains somewhat non-trivial success rates, test-time compute can be used to outperform a 14x larger model.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Optimal Dynamic Compute Allocation Policy)**: Allocating inference FLOPs adaptively based on intrinsic problem hardness rather than uniform fixed rollouts.

- **Challenge 2 (Verifier Hacking & Goodhart's Law in Process Models)**: Repeated sampling over thousands of candidates exploits slight verifier imperfections, favoring degenerately long rationales.

- **Challenge 3 (Step-Level Value Estimation Accuracy)**: Estimating the ground-truth likelihood of reaching a correct answer from intermediate partial states without exhaustive rollouts.

- **Challenge 4 (GPU Memory Pressures in Multi-Branch Tree Exploration)**: Retaining sprawling KV-cache states during wide-branching search trees exhausts GPU VRAM.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
