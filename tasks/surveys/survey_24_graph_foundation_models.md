---
id: survey_24_graph_foundation_models
type: survey
field: graph_and_geometric_ml
title: "A Survey on Graph Foundation Models"
arxiv_id: "2402.02216"
authors: "Mao et al."
source_url: "https://arxiv.org/abs/2402.02216"
pdf_url: "https://arxiv.org/pdf/2402.02216.pdf"
keywords:
  - graph-foundation-models
  - graph-tokenization
  - transferable-gnn
  - graph-transformers
  - heterogeneous-graphs
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---

# A Survey on Graph Foundation Models

## 1. Verified Paper Identity & Links
- **Title**: A Survey on Graph Foundation Models
- **Authors**: Mao et al.
- **arXiv Entry**: [https://arxiv.org/abs/2402.02216](https://arxiv.org/abs/2402.02216)
- **Full PDF**: [https://arxiv.org/pdf/2402.02216.pdf](https://arxiv.org/pdf/2402.02216.pdf)
- **Field**: graph_and_geometric_ml

## 2. Official Paper Abstract
Graph Foundation Models (GFMs) are emerging as a significant research topic in the graph domain, aiming to develop graph models trained on extensive and diverse data to enhance their applicability across various tasks and domains. Developing GFMs presents unique challenges over traditional Graph Neural Networks (GNNs), which are typically trained from scratch for specific tasks on particular datasets. The primary challenge in constructing GFMs lies in effectively leveraging vast and diverse graph data to achieve positive transfer. Drawing inspiration from existing foundation models in the CV and NLP domains, we propose a novel perspective for the GFM development by advocating for a ``graph vocabulary&#39;&#39;, in which the basic transferable units underlying graphs encode the invariance on graphs. We ground the graph vocabulary construction from essential aspects including network analysis, expressiveness, and stability. Such a vocabulary perspective can potentially advance the future GFM design in line with the neural scaling laws. All relevant resources with GFM design can be found here.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Scalability Bottlenecks in graph-foundation-models)**: Computational and memory ceilings when scaling algorithms on high-dimensional inputs.

- **Challenge 2 (Generalization & Distribution Shifts in graph-tokenization)**: Performance degradation when evaluated on out-of-distribution benchmarks and dynamic environments.

- **Challenge 3 (Evaluation Gaps & Alignment with transferable-gnn)**: Disconnect between current proxy metrics and authentic downstream utility.

- **Challenge 4 (Theoretical Foundations of graph-transformers)**: Establishing formal guarantees and provable bounds on convergence and stability.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
