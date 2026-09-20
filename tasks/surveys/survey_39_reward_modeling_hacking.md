---
id: survey_39_reward_modeling_hacking
type: survey
field: trustworthy_and_safety
title: "RewardBench: Evaluating Reward Models for Language Modeling"
arxiv_id: "2403.14809"
authors: "Lambert et al."
source_url: "https://arxiv.org/abs/2403.14809"
pdf_url: "https://arxiv.org/pdf/2403.14809.pdf"
keywords:
  - reward-modeling
  - reward-hacking
  - goodharts-law
  - preference-learning
  - process-rewards
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---

# RewardBench: Evaluating Reward Models for Language Modeling

## 1. Verified Paper Identity & Links
- **Title**: RewardBench: Evaluating Reward Models for Language Modeling
- **Authors**: Lambert et al.
- **arXiv Entry**: [https://arxiv.org/abs/2403.14809](https://arxiv.org/abs/2403.14809)
- **Full PDF**: [https://arxiv.org/pdf/2403.14809.pdf](https://arxiv.org/pdf/2403.14809.pdf)
- **Field**: trustworthy_and_safety

## 2. Official Paper Abstract
The intricate nature of the brain necessitates the application of advanced probing techniques to comprehensively study and understand its working mechanisms. Neurophotonics offers minimally invasive methods to probe the brain using optics at cellular and even molecular levels. However, multiple challenges persist, especially concerning imaging depth, field of view, speed, and biocompatibility. A major hindrance to solving these challenges in optics is the scattering nature of the brain. This perspective highlights the potential of complex media optics, a specialized area of study focused on light propagation in materials with intricate heterogeneous optical properties, in advancing and improving neuronal readouts for structural imaging and optical recordings of neuronal activity. Key strategies include wavefront shaping techniques and computational imaging and sensing techniques that exploit scattering properties for enhanced performance. We discuss the potential merger of the two fields as well as potential challenges and perspectives toward longer term in vivo applications.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Scalability Bottlenecks in reward-modeling)**: Computational and memory ceilings when scaling algorithms on high-dimensional inputs.

- **Challenge 2 (Generalization & Distribution Shifts in reward-hacking)**: Performance degradation when evaluated on out-of-distribution benchmarks and dynamic environments.

- **Challenge 3 (Evaluation Gaps & Alignment with goodharts-law)**: Disconnect between current proxy metrics and authentic downstream utility.

- **Challenge 4 (Theoretical Foundations of preference-learning)**: Establishing formal guarantees and provable bounds on convergence and stability.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
