---
id: survey_50_scientific_hypothesis_generation
type: survey
field: ai_for_science
title: "Scientific discovery in the age of artificial intelligence"
arxiv_id: ""
authors: "Hanchen Wang, Tianfan Fu, Yuanqi Du et al."
source_url: "https://www.nature.com/articles/s41586-023-06221-2"
pdf_url: "https://cs.stanford.edu/~jure/pubs/discovery-nature23.pdf"
keywords:
  - scientific-discovery
  - hypothesis-generation
  - automated-science
  - literature-mining
  - closed-loop-labs
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---
# Scientific discovery in the age of artificial intelligence

## 1. Verified Paper Identity & Links
- **Title**: Scientific discovery in the age of artificial intelligence
- **Authors**: Hanchen Wang, Tianfan Fu, Yuanqi Du et al.
- **Nature Article**: [https://www.nature.com/articles/s41586-023-06221-2](https://www.nature.com/articles/s41586-023-06221-2)
- **Full PDF**: [https://cs.stanford.edu/~jure/pubs/discovery-nature23.pdf](https://cs.stanford.edu/~jure/pubs/discovery-nature23.pdf)
- **Field**: ai_for_science

## 2. Official Paper Abstract
Artificial intelligence (AI) is being increasingly integrated into scientific discovery to augment and accelerate research, helping scientists to generate hypotheses, design experiments, collect and interpret large datasets, and gain insights that might not have been possible using traditional scientific methods alone. Here we examine breakthroughs over the past decade that include self-supervised learning, which allows models to be trained on vast amounts of unlabelled data, and geometric deep learning, which leverages knowledge about the structure of scientific data to enhance model accuracy and efficiency. Generative AI methods can create designs, such as small-molecule drugs and proteins, by analysing diverse data modalities, including images and sequences. We discuss how these methods can help scientists throughout the scientific process and the central issues that remain despite such advances.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Scalability Bottlenecks in scientific-discovery)**: Computational and memory ceilings when scaling algorithms on high-dimensional inputs.

- **Challenge 2 (Generalization & Distribution Shifts in hypothesis-generation)**: Performance degradation when evaluated on out-of-distribution benchmarks and dynamic environments.

- **Challenge 3 (Evaluation Gaps & Alignment with automated-science)**: Disconnect between current proxy metrics and authentic downstream utility.

- **Challenge 4 (Theoretical Foundations of literature-mining)**: Establishing formal guarantees and provable bounds on convergence and stability.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
