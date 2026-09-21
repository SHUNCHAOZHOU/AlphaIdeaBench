---
id: survey_13_ai_for_drug_discovery
type: survey
field: ai_for_science
title: "Artificial Intelligence for Drug Discovery: Are We There Yet?"
arxiv_id: "2307.06521"
authors: "Catrin Hasselgren, Tudor I. Oprea"
source_url: "https://arxiv.org/abs/2307.06521"
pdf_url: "https://arxiv.org/pdf/2307.06521.pdf"
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
# Artificial Intelligence for Drug Discovery: Are We There Yet?

## 1. Verified Paper Identity & Links
- **Title**: Artificial Intelligence for Drug Discovery: Are We There Yet?
- **Authors**: Catrin Hasselgren, Tudor I. Oprea
- **arXiv Entry**: [https://arxiv.org/abs/2307.06521](https://arxiv.org/abs/2307.06521)
- **Full PDF**: [https://arxiv.org/pdf/2307.06521.pdf](https://arxiv.org/pdf/2307.06521.pdf)
- **Field**: ai_for_science

## 2. Official Paper Abstract
Drug discovery is adapting to novel technologies such as data science, informatics, and artificial intelligence (AI) to accelerate effective treatment development while reducing costs and animal experiments. AI is transforming drug discovery, as indicated by increasing interest from investors, industrial and academic scientists, and legislators. Successful drug discovery requires optimizing properties related to pharmacodynamics, pharmacokinetics, and clinical outcomes. This review discusses the use of AI in the three pillars of drug discovery: diseases, targets, and therapeutic modalities, with a focus on small molecule drugs. AI technologies, such as generative chemistry, machine learning, and multi-property optimization, have enabled several compounds to enter clinical trials. The scientific community must carefully vet known information to address the reproducibility crisis. The full potential of AI in drug discovery can only be realized with sufficient ground truth and appropriate human intervention at later pipeline stages.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Synthesizability & Retrosynthetic Feasibility)**: Generative graph models produce topologically valid molecules that are impossible to synthesize via known chemical reactions.

- **Challenge 2 (Protein Flexibility in Pocket-Conditioned Design)**: Treating protein binding pockets as rigid ignores induced-fit conformational changes during drug binding.

- **Challenge 3 (Sparse & Noisy Ground Truth Data)**: Wet-lab binding affinity datasets (PDBbind, ChEMBL) contain significant experimental noise and assay bias.

- **Challenge 4 (Multi-Objective Pareto Optimization)**: Simultaneously satisfying target binding affinity, low toxicity, solubility, and metabolic stability.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
