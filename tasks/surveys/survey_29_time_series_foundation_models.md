---
id: survey_29_time_series_foundation_models
type: survey
field: ai_for_science
title: "Foundation Models for Time Series Analysis: A Tutorial and Survey"
arxiv_id: "2403.14735"
authors: "Yuxuan Liang, Haomin Wen, Yuqi Nie et al."
source_url: "https://arxiv.org/abs/2403.14735"
pdf_url: "https://arxiv.org/pdf/2403.14735.pdf"
keywords:
  - time-series-foundation-models
  - temporal-patching
  - cross-domain-forecasting
  - zero-shot-time-series
  - non-stationarity
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---
# Foundation Models for Time Series Analysis: A Tutorial and Survey

## 1. Verified Paper Identity & Links
- **Title**: Foundation Models for Time Series Analysis: A Tutorial and Survey
- **Authors**: Yuxuan Liang, Haomin Wen, Yuqi Nie et al.
- **arXiv Entry**: [https://arxiv.org/abs/2403.14735](https://arxiv.org/abs/2403.14735)
- **Full PDF**: [https://arxiv.org/pdf/2403.14735.pdf](https://arxiv.org/pdf/2403.14735.pdf)
- **Field**: ai_for_science

## 2. Official Paper Abstract
Time series analysis stands as a focal point within the data mining community, serving as a cornerstone for extracting valuable insights crucial to a myriad of real-world applications. Recent advances in Foundation Models (FMs) have fundamentally reshaped the paradigm of model design for time series analysis, boosting various downstream tasks in practice. These innovative approaches often leverage pre-trained or fine-tuned FMs to harness generalized knowledge tailored for time series analysis. This survey aims to furnish a comprehensive and up-to-date overview of FMs for time series analysis. While prior surveys have predominantly focused on either application or pipeline aspects of FMs in time series analysis, they have often lacked an in-depth understanding of the underlying mechanisms that elucidate why and how FMs benefit time series analysis. To address this gap, our survey adopts a methodology-centric classification, delineating various pivotal elements of time-series FMs, including model architectures, pre-training techniques, adaptation methods, and data modalities. Overall, this survey serves to consolidate the latest advancements in FMs pertinent to time series analysis, accentuating their theoretical underpinnings, recent strides in development, and avenues for future exploration.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Scalability Bottlenecks in time-series-foundation-models)**: Computational and memory ceilings when scaling algorithms on high-dimensional inputs.

- **Challenge 2 (Generalization & Distribution Shifts in temporal-patching)**: Performance degradation when evaluated on out-of-distribution benchmarks and dynamic environments.

- **Challenge 3 (Evaluation Gaps & Alignment with cross-domain-forecasting)**: Disconnect between current proxy metrics and authentic downstream utility.

- **Challenge 4 (Theoretical Foundations of zero-shot-time-series)**: Establishing formal guarantees and provable bounds on convergence and stability.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
