---
id: survey_13_ai_for_drug_discovery
type: survey
field: ai_for_science
title: "Artificial Intelligence in Drug Discovery and Development: A Comprehensive Review"
arxiv_id: "2308.14115"
authors: "Jianan Deng et al."
source_url: "https://arxiv.org/abs/2308.14115"
pdf_url: "https://arxiv.org/pdf/2308.14115.pdf"
keywords:
  - drug-discovery
  - molecular-generation
  - pocket-docking
  - binding-affinity
  - admet-prediction
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---

# Artificial Intelligence in Drug Discovery and Development: A Comprehensive Review

## 1. Verified Paper Identity & Links
- **Title**: Artificial Intelligence in Drug Discovery and Development: A Comprehensive Review
- **Authors**: Jianan Deng et al.
- **arXiv Entry**: [https://arxiv.org/abs/2308.14115](https://arxiv.org/abs/2308.14115)
- **Full PDF**: [https://arxiv.org/pdf/2308.14115.pdf](https://arxiv.org/pdf/2308.14115.pdf)
- **Field**: ai_for_science

## 2. Official Paper Abstract
Natural language is among the most accessible tools for explaining decisions to humans, and large pretrained language models (PLMs) have demonstrated impressive abilities to generate coherent natural language explanations (NLE). The existing NLE research perspectives do not take the audience into account. An NLE can have high textual quality, but it might not accommodate audiences&#39; needs and preference. To address this limitation, we propose an alternative perspective, \textit{situated} NLE. On the evaluation side, we set up automated evaluation scores. These scores describe the properties of NLEs in lexical, semantic, and pragmatic categories. On the generation side, we identify three prompt engineering techniques and assess their applicability on the situations. Situated NLE provides a perspective and facilitates further research on the generation and evaluation of explanations.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Synthesizability & Retrosynthetic Feasibility)**: Generative graph models produce topologically valid molecules that are impossible to synthesize via known chemical reactions.

- **Challenge 2 (Protein Flexibility in Pocket-Conditioned Design)**: Treating protein binding pockets as rigid ignores induced-fit conformational changes during drug binding.

- **Challenge 3 (Sparse & Noisy Ground Truth Data)**: Wet-lab binding affinity datasets (PDBbind, ChEMBL) contain significant experimental noise and assay bias.

- **Challenge 4 (Multi-Objective Pareto Optimization)**: Simultaneously satisfying target binding affinity, low toxicity, solubility, and metabolic stability.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
