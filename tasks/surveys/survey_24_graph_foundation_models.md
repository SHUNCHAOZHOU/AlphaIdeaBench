---
id: survey_24_graph_foundation_models
type: survey
field: graph_and_geometric_ml
title: "Graph Foundation Models: Concepts, Opportunities and Challenges"
arxiv_id: "2310.11829"
authors: "Jiawei Liu, Cheng Yang, Zhiyuan Lu et al."
source_url: "https://arxiv.org/abs/2310.11829"
pdf_url: "https://arxiv.org/pdf/2310.11829.pdf"
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
# Graph Foundation Models: Concepts, Opportunities and Challenges

## 1. Verified Paper Identity & Links
- **Title**: Graph Foundation Models: Concepts, Opportunities and Challenges
- **Authors**: Jiawei Liu, Cheng Yang, Zhiyuan Lu et al.
- **arXiv Entry**: [https://arxiv.org/abs/2310.11829](https://arxiv.org/abs/2310.11829)
- **Full PDF**: [https://arxiv.org/pdf/2310.11829.pdf](https://arxiv.org/pdf/2310.11829.pdf)
- **Field**: graph_and_geometric_ml

## 2. Official Paper Abstract
Foundation models have emerged as critical components in a variety of artificial intelligence applications, and showcase significant success in natural language processing and several other domains. Meanwhile, the field of graph machine learning is witnessing a paradigm transition from shallow methods to more sophisticated deep learning approaches. The capabilities of foundation models in generalization and adaptation motivate graph machine learning researchers to discuss the potential of developing a new graph learning paradigm. This paradigm envisions models that are pre-trained on extensive graph data and can be adapted for various graph tasks. Despite this burgeoning interest, there is a noticeable lack of clear definitions and systematic analyses pertaining to this new domain. To this end, this article introduces the concept of Graph Foundation Models (GFMs), and offers an exhaustive explanation of their key characteristics and underlying technologies. We proceed to classify the existing work related to GFMs into three distinct categories, based on their dependence on graph neural networks and large language models. In addition to providing a thorough review of the current state of GFMs, this article also outlooks potential avenues for future research in this rapidly evolving domain.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Scalability Bottlenecks in graph-foundation-models)**: Computational and memory ceilings when scaling algorithms on high-dimensional inputs.

- **Challenge 2 (Generalization & Distribution Shifts in graph-tokenization)**: Performance degradation when evaluated on out-of-distribution benchmarks and dynamic environments.

- **Challenge 3 (Evaluation Gaps & Alignment with transferable-gnn)**: Disconnect between current proxy metrics and authentic downstream utility.

- **Challenge 4 (Theoretical Foundations of graph-transformers)**: Establishing formal guarantees and provable bounds on convergence and stability.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
