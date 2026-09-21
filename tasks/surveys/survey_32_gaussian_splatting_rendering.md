---
id: survey_32_gaussian_splatting_rendering
type: survey
field: multimodal_and_cv
title: "A Survey on 3D Gaussian Splatting"
arxiv_id: "2401.03890"
authors: "Guikun Chen, Wenguan Wang"
source_url: "https://arxiv.org/abs/2401.03890"
pdf_url: "https://arxiv.org/pdf/2401.03890.pdf"
keywords:
  - 3d-gaussian-splatting
  - neural-rendering
  - dynamic-scenes
  - view-synthesis
  - memory-optimization
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---
# A Survey on 3D Gaussian Splatting

## 1. Verified Paper Identity & Links
- **Title**: A Survey on 3D Gaussian Splatting
- **Authors**: Guikun Chen, Wenguan Wang
- **arXiv Entry**: [https://arxiv.org/abs/2401.03890](https://arxiv.org/abs/2401.03890)
- **Full PDF**: [https://arxiv.org/pdf/2401.03890.pdf](https://arxiv.org/pdf/2401.03890.pdf)
- **Field**: multimodal_and_cv

## 2. Official Paper Abstract
3D Gaussian splatting (GS) has emerged as a transformative technique in radiance fields. Unlike mainstream implicit neural models, 3D GS uses millions of learnable 3D Gaussians for an explicit scene representation. Paired with a differentiable rendering algorithm, this approach achieves real-time rendering and unprecedented editability, making it a potential game-changer for 3D reconstruction and representation. In the present paper, we provide the first systematic overview of the recent developments and critical contributions in 3D GS. We begin with a detailed exploration of the underlying principles and the driving forces behind the emergence of 3D GS, laying the groundwork for understanding its significance. A focal point of our discussion is the practical applicability of 3D GS. By enabling unprecedented rendering speed, 3D GS opens up a plethora of applications, ranging from virtual reality to interactive media and beyond. This is complemented by a comparative analysis of leading 3D GS models, evaluated across various benchmark tasks to highlight their performance and practical utility. The survey concludes by identifying current challenges and suggesting potential avenues for future research. Through this survey, we aim to provide a valuable resource for both newcomers and seasoned researchers, fostering further exploration and advancement in explicit radiance field.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Scalability Bottlenecks in 3d-gaussian-splatting)**: Computational and memory ceilings when scaling algorithms on high-dimensional inputs.

- **Challenge 2 (Generalization & Distribution Shifts in neural-rendering)**: Performance degradation when evaluated on out-of-distribution benchmarks and dynamic environments.

- **Challenge 3 (Evaluation Gaps & Alignment with dynamic-scenes)**: Disconnect between current proxy metrics and authentic downstream utility.

- **Challenge 4 (Theoretical Foundations of view-synthesis)**: Establishing formal guarantees and provable bounds on convergence and stability.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
