---
id: survey_14_diffusion_3d_generation
type: survey
field: multimodal_and_cv
title: "A Survey on 3D Generative Diffusion Models"
arxiv_id: "2403.04780"
authors: "Hao-Kang Liu et al."
source_url: "https://arxiv.org/abs/2403.04780"
pdf_url: "https://arxiv.org/pdf/2403.04780.pdf"
keywords:
  - 3d-generation
  - score-distillation-sampling
  - 3d-gaussian-splatting
  - 4d-dynamics
  - janus-problem
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---

# A Survey on 3D Generative Diffusion Models

## 1. Verified Paper Identity & Links
- **Title**: A Survey on 3D Generative Diffusion Models
- **Authors**: Hao-Kang Liu et al.
- **arXiv Entry**: [https://arxiv.org/abs/2403.04780](https://arxiv.org/abs/2403.04780)
- **Full PDF**: [https://arxiv.org/pdf/2403.04780.pdf](https://arxiv.org/pdf/2403.04780.pdf)
- **Field**: multimodal_and_cv

## 2. Official Paper Abstract
Graphs with abundant attributes are essential in modeling interconnected entities and enhancing predictions across various real-world applications. Traditional Graph Neural Networks (GNNs) often require re-training for different graph tasks and datasets. Although the emergence of Large Language Models (LLMs) has introduced new paradigms in natural language processing, their potential for generic graph mining, training a single model to simultaneously handle diverse tasks and datasets, remains under-explored. To this end, our novel framework MuseGraph, seamlessly integrates the strengths of GNNs and LLMs into one foundation model for graph mining across tasks and datasets. This framework first features a compact graph description to encapsulate key graph information within language token limitations. Then, we propose a diverse instruction generation mechanism with Chain-of-Thought (CoT)-based instruction packages to distill the reasoning capabilities from advanced LLMs like GPT-4. Finally, we design a graph-aware instruction tuning strategy to facilitate mutual enhancement across multiple tasks and datasets while preventing catastrophic forgetting of LLMs&#39; generative abilities. Our experimental results demonstrate significant improvements in five graph tasks and ten datasets, showcasing the potential of our MuseGraph in enhancing the accuracy of graph-oriented downstream tasks while improving the generation abilities of LLMs.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (The Multi-Faced Janus Problem)**: 2D score distillation lacks 3D geometric awareness, producing multiple faces or heads on symmetric objects.

- **Challenge 2 (Scarcity of High-Resolution 3D Data)**: Severe shortage of dense, diverse, clean 3D mesh datasets compared to billions of 2D images.

- **Challenge 3 (Temporal Coherence in Dynamic 4D Generation)**: Extending 3D representations to 4D time sequences induces flickering deformations and unnatural kinematics.

- **Challenge 4 (Disentanglement of Material and Lighting)**: Inability to separate diffuse color, specular roughness, and environmental lighting during novel view synthesis.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
