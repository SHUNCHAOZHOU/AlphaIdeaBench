---
id: survey_42_molecular_dynamics_genai
type: survey
field: ai_for_science
title: "A Survey on Graph Diffusion Models: Generative AI in Science for Molecule, Protein and Material"
arxiv_id: "2304.01565"
authors: "Mengchun Zhang, Maryam Qamar, Taegoo Kang et al."
source_url: "https://arxiv.org/abs/2304.01565"
pdf_url: "https://arxiv.org/pdf/2304.01565.pdf"
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
# A Survey on Graph Diffusion Models: Generative AI in Science for Molecule, Protein and Material

## 1. Verified Paper Identity & Links
- **Title**: A Survey on Graph Diffusion Models: Generative AI in Science for Molecule, Protein and Material
- **Authors**: Mengchun Zhang, Maryam Qamar, Taegoo Kang et al.
- **arXiv Entry**: [https://arxiv.org/abs/2304.01565](https://arxiv.org/abs/2304.01565)
- **Full PDF**: [https://arxiv.org/pdf/2304.01565.pdf](https://arxiv.org/pdf/2304.01565.pdf)
- **Field**: ai_for_science

## 2. Official Paper Abstract
Diffusion models have become a new SOTA generative modeling method in various fields, for which there are multiple survey works that provide an overall survey. With the number of articles on diffusion models increasing exponentially in the past few years, there is an increasing need for surveys of diffusion models on specific fields. In this work, we are committed to conducting a survey on the graph diffusion models. Even though our focus is to cover the progress of diffusion models in graphs, we first briefly summarize how other generative modeling methods are used for graphs. After that, we introduce the mechanism of diffusion models in various forms, which facilitates the discussion on the graph diffusion models. The applications of graph diffusion models mainly fall into the category of AI-generated content (AIGC) in science, for which we mainly focus on how graph diffusion models are utilized for generating molecules and proteins but also cover other cases, including materials design. Moreover, we discuss the issue of evaluating diffusion models in the graph domain and the existing challenges.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Scalability Bottlenecks in molecular-dynamics)**: Computational and memory ceilings when scaling algorithms on high-dimensional inputs.

- **Challenge 2 (Generalization & Distribution Shifts in conformational-sampling)**: Performance degradation when evaluated on out-of-distribution benchmarks and dynamic environments.

- **Challenge 3 (Evaluation Gaps & Alignment with boltzmann-generators)**: Disconnect between current proxy metrics and authentic downstream utility.

- **Challenge 4 (Theoretical Foundations of so3-equivariance)**: Establishing formal guarantees and provable bounds on convergence and stability.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
