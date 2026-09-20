---
id: survey_42_molecular_dynamics_genai
type: survey
field: ai_for_science
title: "Generative Diffusion Models for Molecular Conformations: A Survey"
arxiv_id: "2305.01401"
authors: "Arts et al."
source_url: "https://arxiv.org/abs/2305.01401"
pdf_url: "https://arxiv.org/pdf/2305.01401.pdf"
keywords:
  - molecular-dynamics
  - conformational-sampling
  - boltzmann-generators
  - so3-equivariance
  - free-energy-estimation
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---

# Generative Diffusion Models for Molecular Conformations: A Survey

## 1. Verified Paper Identity & Links
- **Title**: Generative Diffusion Models for Molecular Conformations: A Survey
- **Authors**: Arts et al.
- **arXiv Entry**: [https://arxiv.org/abs/2305.01401](https://arxiv.org/abs/2305.01401)
- **Full PDF**: [https://arxiv.org/pdf/2305.01401.pdf](https://arxiv.org/pdf/2305.01401.pdf)
- **Field**: ai_for_science

## 2. Official Paper Abstract
Machine-learning potentials provide computationally efficient and accurate approximations of the Born-Oppenheimer potential energy surface. This potential determines many materials properties and simulation techniques usually require its gradients, in particular forces and stress for molecular dynamics, and heat flux for thermal transport properties. Recently developed potentials feature high body order and can include equivariant semi-local interactions through message-passing mechanisms. Due to their complex functional forms, they rely on automatic differentiation (AD), overcoming the need for manual implementations or finite-difference schemes to evaluate gradients. This study demonstrates a unified AD approach to obtain forces, stress, and heat flux for such potentials, and provides a model-independent implementation. The method is tested on the Lennard-Jones potential, and then applied to predict cohesive properties and thermal conductivity of tin selenide using an equivariant message-passing neural network potential.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Scalability Bottlenecks in molecular-dynamics)**: Computational and memory ceilings when scaling algorithms on high-dimensional inputs.

- **Challenge 2 (Generalization & Distribution Shifts in conformational-sampling)**: Performance degradation when evaluated on out-of-distribution benchmarks and dynamic environments.

- **Challenge 3 (Evaluation Gaps & Alignment with boltzmann-generators)**: Disconnect between current proxy metrics and authentic downstream utility.

- **Challenge 4 (Theoretical Foundations of so3-equivariance)**: Establishing formal guarantees and provable bounds on convergence and stability.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
