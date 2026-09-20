---
id: survey_37_tabular_deep_learning
type: survey
field: interpretability_and_theory
title: "Why do tree-based models still outperform deep learning on tabular data?"
arxiv_id: "2207.08815"
authors: "Grinsztajn et al."
source_url: "https://arxiv.org/abs/2207.08815"
pdf_url: "https://arxiv.org/pdf/2207.08815.pdf"
keywords:
  - tabular-deep-learning
  - xgboost
  - tree-based-models
  - tabpfn
  - inductive-biases
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---

# Why do tree-based models still outperform deep learning on tabular data?

## 1. Verified Paper Identity & Links
- **Title**: Why do tree-based models still outperform deep learning on tabular data?
- **Authors**: Grinsztajn et al.
- **arXiv Entry**: [https://arxiv.org/abs/2207.08815](https://arxiv.org/abs/2207.08815)
- **Full PDF**: [https://arxiv.org/pdf/2207.08815.pdf](https://arxiv.org/pdf/2207.08815.pdf)
- **Field**: interpretability_and_theory

## 2. Official Paper Abstract
While deep learning has enabled tremendous progress on text and image datasets, its superiority on tabular data is not clear. We contribute extensive benchmarks of standard and novel deep learning methods as well as tree-based models such as XGBoost and Random Forests, across a large number of datasets and hyperparameter combinations. We define a standard set of 45 datasets from varied domains with clear characteristics of tabular data and a benchmarking methodology accounting for both fitting models and finding good hyperparameters. Results show that tree-based models remain state-of-the-art on medium-sized data ($\sim$10K samples) even without accounting for their superior speed. To understand this gap, we conduct an empirical investigation into the differing inductive biases of tree-based models and Neural Networks (NNs). This leads to a series of challenges which should guide researchers aiming to build tabular-specific NNs: 1. be robust to uninformative features, 2. preserve the orientation of the data, and 3. be able to easily learn irregular functions. To stimulate research on tabular architectures, we contribute a standard benchmark and raw data for baselines: every point of a 20 000 compute hours hyperparameter search for each learner.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Scalability Bottlenecks in tabular-deep-learning)**: Computational and memory ceilings when scaling algorithms on high-dimensional inputs.

- **Challenge 2 (Generalization & Distribution Shifts in xgboost)**: Performance degradation when evaluated on out-of-distribution benchmarks and dynamic environments.

- **Challenge 3 (Evaluation Gaps & Alignment with tree-based-models)**: Disconnect between current proxy metrics and authentic downstream utility.

- **Challenge 4 (Theoretical Foundations of tabpfn)**: Establishing formal guarantees and provable bounds on convergence and stability.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
