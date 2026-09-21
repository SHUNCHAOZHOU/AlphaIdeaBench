---
id: survey_43_autonomous_driving_foundation_models
type: survey
field: multimodal_and_cv
title: "A Survey for Foundation Models in Autonomous Driving"
arxiv_id: "2402.01105"
authors: "Haoxiang Gao, Zhongruo Wang, Yaqian Li et al."
source_url: "https://arxiv.org/abs/2402.01105"
pdf_url: "https://arxiv.org/pdf/2402.01105.pdf"
keywords:
  - autonomous-driving
  - end-to-end-driving
  - bev-perception
  - world-models-ad
  - trajectory-planning
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---
# A Survey for Foundation Models in Autonomous Driving

## 1. Verified Paper Identity & Links
- **Title**: A Survey for Foundation Models in Autonomous Driving
- **Authors**: Haoxiang Gao, Zhongruo Wang, Yaqian Li et al.
- **arXiv Entry**: [https://arxiv.org/abs/2402.01105](https://arxiv.org/abs/2402.01105)
- **Full PDF**: [https://arxiv.org/pdf/2402.01105.pdf](https://arxiv.org/pdf/2402.01105.pdf)
- **Field**: multimodal_and_cv

## 2. Official Paper Abstract
The advent of foundation models has revolutionized the fields of natural language processing and computer vision, paving the way for their application in autonomous driving (AD). This survey presents a comprehensive review of more than 40 research papers, demonstrating the role of foundation models in enhancing AD. Large language models contribute to planning and simulation in AD, particularly through their proficiency in reasoning, code generation and translation. In parallel, vision foundation models are increasingly adapted for critical tasks such as 3D object detection and tracking, as well as creating realistic driving scenarios for simulation and testing. Multi-modal foundation models, integrating diverse inputs, exhibit exceptional visual understanding and spatial reasoning, crucial for end-to-end AD. This survey not only provides a structured taxonomy, categorizing foundation models based on their modalities and functionalities within the AD domain but also delves into the methods employed in current research. It identifies the gaps between existing foundation models and cutting-edge AD approaches, thereby charting future research directions and proposing a roadmap for bridging these gaps.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Scalability Bottlenecks in autonomous-driving)**: Computational and memory ceilings when scaling algorithms on high-dimensional inputs.

- **Challenge 2 (Generalization & Distribution Shifts in end-to-end-driving)**: Performance degradation when evaluated on out-of-distribution benchmarks and dynamic environments.

- **Challenge 3 (Evaluation Gaps & Alignment with bev-perception)**: Disconnect between current proxy metrics and authentic downstream utility.

- **Challenge 4 (Theoretical Foundations of world-models-ad)**: Establishing formal guarantees and provable bounds on convergence and stability.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
