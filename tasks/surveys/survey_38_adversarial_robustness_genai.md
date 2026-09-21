---
id: survey_38_adversarial_robustness_genai
type: survey
field: trustworthy_and_safety
title: "RobustBench: a standardized adversarial robustness benchmark"
arxiv_id: "2010.09670"
authors: "Francesco Croce, Maksym Andriushchenko, Vikash Sehwag et al."
source_url: "https://arxiv.org/abs/2010.09670"
pdf_url: "https://arxiv.org/pdf/2010.09670.pdf"
keywords:
  - adversarial-robustness
  - certified-defenses
  - adversarial-training
  - continuous-perturbations
  - multimodal-attacks
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---
# RobustBench: a standardized adversarial robustness benchmark

## 1. Verified Paper Identity & Links
- **Title**: RobustBench: a standardized adversarial robustness benchmark
- **Authors**: Francesco Croce, Maksym Andriushchenko, Vikash Sehwag et al.
- **arXiv Entry**: [https://arxiv.org/abs/2010.09670](https://arxiv.org/abs/2010.09670)
- **Full PDF**: [https://arxiv.org/pdf/2010.09670.pdf](https://arxiv.org/pdf/2010.09670.pdf)
- **Field**: trustworthy_and_safety

## 2. Official Paper Abstract
As a research community, we are still lacking a systematic understanding of the progress on adversarial robustness which often makes it hard to identify the most promising ideas in training robust models. A key challenge in benchmarking robustness is that its evaluation is often error-prone leading to robustness overestimation. Our goal is to establish a standardized benchmark of adversarial robustness, which as accurately as possible reflects the robustness of the considered models within a reasonable computational budget. To this end, we start by considering the image classification task and introduce restrictions (possibly loosened in the future) on the allowed models. We evaluate adversarial robustness with AutoAttack, an ensemble of white- and black-box attacks, which was recently shown in a large-scale study to improve almost all robustness evaluations compared to the original publications. To prevent overadaptation of new defenses to AutoAttack, we welcome external evaluations based on adaptive attacks, especially where AutoAttack flags a potential overestimation of robustness. Our leaderboard, hosted at https://robustbench.github.io/, contains evaluations of 120+ models and aims at reflecting the current state of the art in image classification on a set of well-defined tasks in $\ell_\infty$- and $\ell_2$-threat models and on common corruptions, with possible extensions in the future. Additionally, we open-source the library https://github.com/RobustBench/robustbench that provides unified access to 80+ robust models to facilitate their downstream applications. Finally, based on the collected models, we analyze the impact of robustness on the performance on distribution shifts, calibration, out-of-distribution detection, fairness, privacy leakage, smoothness, and transferability.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Scalability Bottlenecks in adversarial-robustness)**: Computational and memory ceilings when scaling algorithms on high-dimensional inputs.

- **Challenge 2 (Generalization & Distribution Shifts in certified-defenses)**: Performance degradation when evaluated on out-of-distribution benchmarks and dynamic environments.

- **Challenge 3 (Evaluation Gaps & Alignment with adversarial-training)**: Disconnect between current proxy metrics and authentic downstream utility.

- **Challenge 4 (Theoretical Foundations of continuous-perturbations)**: Establishing formal guarantees and provable bounds on convergence and stability.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
