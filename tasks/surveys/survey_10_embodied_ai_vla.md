---
id: survey_10_embodied_ai_vla
type: survey
field: robotics_and_rl
title: "A Survey on Vision-Language-Action Models for Embodied AI"
arxiv_id: "2405.14093"
authors: "Yueen Ma, Zixing Song, Yuzheng Zhuang et al."
source_url: "https://arxiv.org/abs/2405.14093"
pdf_url: "https://arxiv.org/pdf/2405.14093.pdf"
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
- **Authors**: Yueen Ma, Zixing Song, Yuzheng Zhuang et al.
- **arXiv Entry**: [https://arxiv.org/abs/2405.14093](https://arxiv.org/abs/2405.14093)
- **Full PDF**: [https://arxiv.org/pdf/2405.14093.pdf](https://arxiv.org/pdf/2405.14093.pdf)
- **Field**: robotics_and_rl

## 2. Official Paper Abstract
Embodied AI is widely recognized as a cornerstone of artificial general intelligence (AGI) because it involves controlling embodied agents to perform tasks in the physical world. Building on the success of large language models (LLMs) and vision-language models (VLMs), a new category of multimodal models -- referred to as vision-language-action (VLA) models -- has emerged to address language-conditioned robotic tasks in embodied AI by leveraging their distinct ability to generate actions. The recent proliferation of VLAs necessitates a comprehensive survey to capture the rapidly evolving landscape. To this end, we present the first survey on VLAs for embodied AI. This work provides a detailed taxonomy of VLAs, organized into three major lines of research. The first line focuses on individual components of VLAs. The second line is dedicated to developing VLA-based control policies adept at predicting low-level actions. The third line comprises high-level task planners capable of decomposing long-horizon tasks into a sequence of subtasks, thereby guiding VLAs to follow more general user instructions. Furthermore, we provide an extensive summary of relevant resources, including datasets, simulators, and benchmarks. Finally, we discuss the challenges facing VLAs and outline promising future directions in embodied AI. A curated repository associated with this survey is available at: https://github.com/yueen-ma/Awesome-VLA.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (3D Spatial Affordance & Depth Grounding)**: 2D visual tokens lack explicit 3D spatial geometry, causing grasp depth errors in occluded environments.

- **Challenge 2 (Action Tokenization Quantization Bottlenecks)**: Discretizing continuous 7-DoF motor actions into language tokens causes jerky trajectories unsuitable for delicate contact tasks.

- **Challenge 3 (Generalization to Dynamic Physical Properties)**: Failure when interacting with deformable, slippery, or heavy objects differing from demonstration data.

- **Challenge 4 (Real-Time Sensorimotor Control Latency)**: Autoregressive generation latency (>200ms) is too slow for dynamic closed-loop stabilization (>50Hz).

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
