---
id: survey_10_embodied_ai_vla
type: survey
field: robotics_and_rl
title: "A Survey on Vision-Language-Action Models for Embodied AI"
arxiv_id: "2405.06431"
authors: "Guanzhi Wang, Yuqi Xie et al."
source_url: "https://arxiv.org/abs/2405.06431"
pdf_url: "https://arxiv.org/pdf/2405.06431.pdf"
keywords:
  - embodied-ai
  - vision-language-action
  - robot-manipulation
  - spatial-affordance
  - sim-to-real
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---

# A Survey on Vision-Language-Action Models for Embodied AI

## 1. Verified Paper Identity & Links
- **Title**: A Survey on Vision-Language-Action Models for Embodied AI
- **Authors**: Guanzhi Wang, Yuqi Xie et al.
- **arXiv Entry**: [https://arxiv.org/abs/2405.06431](https://arxiv.org/abs/2405.06431)
- **Full PDF**: [https://arxiv.org/pdf/2405.06431.pdf](https://arxiv.org/pdf/2405.06431.pdf)
- **Field**: robotics_and_rl

## 2. Official Paper Abstract
Y Cam is classified as one of the oscillating Eclipsing Algol (oEA) systems, which feature a $\delta$ Scuti-type pulsating component alongside mass transfer phenomena. oEA systems are invaluable for probing the evolutionary processes and internal structures of binary components offering insights through their binary variations and oscillating. In this study, we conducted a comprehensive investigation of Y Cam utilizing high-quality photometric TESS data, and high-resolution ELODIE spectra. Through our analysis, we examined the radial velocity variation, performed binary modeling, and calculated the effective temperature values of binary components. The fundamental stellar parameters, such as mass and radius, were determined with an accuracy of $\sim$ $2-6$ %. Furthermore, we examined the orbital period variation to assess the amount of mass transfer using the available minima times of the system and three new minima times obtained from TESS light curves. Analyzing the pulsation structure of the system with the TESS data revealed the dominant pulsation period and amplitude of the pulsating component to be 0.066 d and 4.65 mmag, respectively. Notably, we observed frequency modulations with the orbital period&#39;s frequency, along with variations in the amplitude of the highest amplitude frequency across different orbital phases. Remarkably, the amplitude reaches its peak at phases 0.5 and 1. These findings indicate a candidate of a tidally tilted pulsator. Consequently, we investigated the evolutionary status of the binary components using MESA binary evolution models, determining the age of the system to be 3.28 $\pm$ 0.09 Gyr.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (3D Spatial Affordance & Depth Grounding)**: 2D visual tokens lack explicit 3D spatial geometry, causing grasp depth errors in occluded environments.

- **Challenge 2 (Action Tokenization Quantization Bottlenecks)**: Discretizing continuous 7-DoF motor actions into language tokens causes jerky trajectories unsuitable for delicate contact tasks.

- **Challenge 3 (Generalization to Dynamic Physical Properties)**: Failure when interacting with deformable, slippery, or heavy objects differing from demonstration data.

- **Challenge 4 (Real-Time Sensorimotor Control Latency)**: Autoregressive generation latency (>200ms) is too slow for dynamic closed-loop stabilization (>50Hz).

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
