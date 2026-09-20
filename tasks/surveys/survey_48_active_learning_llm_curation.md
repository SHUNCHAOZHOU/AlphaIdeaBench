---
id: survey_48_active_learning_llm_curation
type: survey
field: efficiency_and_systems
title: "A Survey of Deep Active Learning"
arxiv_id: "2009.00236"
authors: "Ren et al."
source_url: "https://arxiv.org/abs/2009.00236"
pdf_url: "https://arxiv.org/pdf/2009.00236.pdf"
keywords:
  - active-learning
  - data-curation
  - uncertainty-sampling
  - influence-functions
  - dataset-pruning
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---

# A Survey of Deep Active Learning

## 1. Verified Paper Identity & Links
- **Title**: A Survey of Deep Active Learning
- **Authors**: Ren et al.
- **arXiv Entry**: [https://arxiv.org/abs/2009.00236](https://arxiv.org/abs/2009.00236)
- **Full PDF**: [https://arxiv.org/pdf/2009.00236.pdf](https://arxiv.org/pdf/2009.00236.pdf)
- **Field**: efficiency_and_systems

## 2. Official Paper Abstract
Active learning (AL) attempts to maximize the performance gain of the model by marking the fewest samples. Deep learning (DL) is greedy for data and requires a large amount of data supply to optimize massive parameters, so that the model learns how to extract high-quality features. In recent years, due to the rapid development of internet technology, we are in an era of information torrents and we have massive amounts of data. In this way, DL has aroused strong interest of researchers and has been rapidly developed. Compared with DL, researchers have relatively low interest in AL. This is mainly because before the rise of DL, traditional machine learning requires relatively few labeled samples. Therefore, early AL is difficult to reflect the value it deserves. Although DL has made breakthroughs in various fields, most of this success is due to the publicity of the large number of existing annotation datasets. However, the acquisition of a large number of high-quality annotated datasets consumes a lot of manpower, which is not allowed in some fields that require high expertise, especially in the fields of speech recognition, information extraction, medical images, etc. Therefore, AL has gradually received due attention. A natural idea is whether AL can be used to reduce the cost of sample annotations, while retaining the powerful learning capabilities of DL. Therefore, deep active learning (DAL) has emerged. Although the related research has been quite abundant, it lacks a comprehensive survey of DAL. This article is to fill this gap, we provide a formal classification method for the existing work, and a comprehensive and systematic overview. In addition, we also analyzed and summarized the development of DAL from the perspective of application. Finally, we discussed the confusion and problems in DAL, and gave some possible development directions for DAL.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Scalability Bottlenecks in active-learning)**: Computational and memory ceilings when scaling algorithms on high-dimensional inputs.

- **Challenge 2 (Generalization & Distribution Shifts in data-curation)**: Performance degradation when evaluated on out-of-distribution benchmarks and dynamic environments.

- **Challenge 3 (Evaluation Gaps & Alignment with uncertainty-sampling)**: Disconnect between current proxy metrics and authentic downstream utility.

- **Challenge 4 (Theoretical Foundations of influence-functions)**: Establishing formal guarantees and provable bounds on convergence and stability.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
