---
id: survey_15_pinns_neural_operators
type: survey
field: ai_for_science
title: "Physics-Informed Machine Learning: A Survey on Problems, Methods and Applications"
arxiv_id: "2211.08064"
authors: "Zhongkai Hao, Songming Liu, Yichi Zhang et al."
source_url: "https://arxiv.org/abs/2211.08064"
pdf_url: "https://arxiv.org/pdf/2211.08064.pdf"
keywords:
  - physics-informed-neural-networks
  - neural-operators
  - fno
  - pde-solvers
  - multiscale-physics
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---
# Physics-Informed Machine Learning: A Survey on Problems, Methods and Applications

## 1. Verified Paper Identity & Links
- **Title**: Physics-Informed Machine Learning: A Survey on Problems, Methods and Applications
- **Authors**: Zhongkai Hao, Songming Liu, Yichi Zhang et al.
- **arXiv Entry**: [https://arxiv.org/abs/2211.08064](https://arxiv.org/abs/2211.08064)
- **Full PDF**: [https://arxiv.org/pdf/2211.08064.pdf](https://arxiv.org/pdf/2211.08064.pdf)
- **Field**: ai_for_science

## 2. Official Paper Abstract
Recent advances of data-driven machine learning have revolutionized fields like computer vision, reinforcement learning, and many scientific and engineering domains. In many real-world and scientific problems, systems that generate data are governed by physical laws. Recent work shows that it provides potential benefits for machine learning models by incorporating the physical prior and collected data, which makes the intersection of machine learning and physics become a prevailing paradigm. By integrating the data and mathematical physics models seamlessly, it can guide the machine learning model towards solutions that are physically plausible, improving accuracy and efficiency even in uncertain and high-dimensional contexts. In this survey, we present this learning paradigm called Physics-Informed Machine Learning (PIML) which is to build a model that leverages empirical data and available physical prior knowledge to improve performance on a set of tasks that involve a physical mechanism. We systematically review the recent development of physics-informed machine learning from three perspectives of machine learning tasks, representation of physical prior, and methods for incorporating physical prior. We also propose several important open research problems based on the current trends in the field. We argue that encoding different forms of physical prior into model architectures, optimizers, inference algorithms, and significant domain-specific applications like inverse engineering design and robotic control is far from being fully explored in the field of physics-informed machine learning. We believe that the interdisciplinary research of physics-informed machine learning will significantly propel research progress, foster the creation of more effective machine learning models, and also offer invaluable assistance in addressing long-standing problems in related disciplines.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Stiff PDE Gradient Imbalance)**: Disparate gradient magnitudes between PDE residuals and boundary conditions trap optimizers in trivial zero solutions.

- **Challenge 2 (High-Frequency Turbulence & Shocks)**: Neural operators act as low-pass filters, losing sharp shockwaves and turbulent vortex dynamics.

- **Challenge 3 (Generalization to Irregular 3D Geometries)**: Generalizing across complex industrial CAD geometries without retraining remains difficult.

- **Challenge 4 (Compounding Error in Long Temporal Rollouts)**: Autoregressive neural solvers accumulate error drift rapidly over extended physical simulation rollouts.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
