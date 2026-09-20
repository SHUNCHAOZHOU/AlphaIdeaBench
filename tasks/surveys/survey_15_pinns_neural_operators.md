---
id: survey_15_pinns_neural_operators
type: survey
field: ai_for_science
title: "Physics-Informed Machine Learning: A Survey on Problems and Methods"
arxiv_id: "2111.03794"
authors: "George Em Karniadakis et al."
source_url: "https://arxiv.org/abs/2111.03794"
pdf_url: "https://arxiv.org/pdf/2111.03794.pdf"
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

# Physics-Informed Machine Learning: A Survey on Problems and Methods

## 1. Verified Paper Identity & Links
- **Title**: Physics-Informed Machine Learning: A Survey on Problems and Methods
- **Authors**: George Em Karniadakis et al.
- **arXiv Entry**: [https://arxiv.org/abs/2111.03794](https://arxiv.org/abs/2111.03794)
- **Full PDF**: [https://arxiv.org/pdf/2111.03794.pdf](https://arxiv.org/pdf/2111.03794.pdf)
- **Field**: ai_for_science

## 2. Official Paper Abstract
In this paper, we propose physics-informed neural operators (PINO) that combine training data and physics constraints to learn the solution operator of a given family of parametric Partial Differential Equations (PDE). PINO is the first hybrid approach incorporating data and PDE constraints at different resolutions to learn the operator. Specifically, in PINO, we combine coarse-resolution training data with PDE constraints imposed at a higher resolution. The resulting PINO model can accurately approximate the ground-truth solution operator for many popular PDE families and shows no degradation in accuracy even under zero-shot super-resolution, i.e., being able to predict beyond the resolution of training data. PINO uses the Fourier neural operator (FNO) framework that is guaranteed to be a universal approximator for any continuous operator and discretization-convergent in the limit of mesh refinement. By adding PDE constraints to FNO at a higher resolution, we obtain a high-fidelity reconstruction of the ground-truth operator. Moreover, PINO succeeds in settings where no training data is available and only PDE constraints are imposed, while previous approaches, such as the Physics-Informed Neural Network (PINN), fail due to optimization challenges, e.g., in multi-scale dynamic systems such as Kolmogorov flows.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Stiff PDE Gradient Imbalance)**: Disparate gradient magnitudes between PDE residuals and boundary conditions trap optimizers in trivial zero solutions.

- **Challenge 2 (High-Frequency Turbulence & Shocks)**: Neural operators act as low-pass filters, losing sharp shockwaves and turbulent vortex dynamics.

- **Challenge 3 (Generalization to Irregular 3D Geometries)**: Generalizing across complex industrial CAD geometries without retraining remains difficult.

- **Challenge 4 (Compounding Error in Long Temporal Rollouts)**: Autoregressive neural solvers accumulate error drift rapidly over extended physical simulation rollouts.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
