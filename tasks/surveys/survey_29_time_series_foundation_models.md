---
id: survey_29_time_series_foundation_models
type: survey
field: ai_for_science
title: "Time Series Foundation Models: A Comprehensive Survey"
arxiv_id: "2402.01801"
authors: "Jin et al."
source_url: "https://arxiv.org/abs/2402.01801"
pdf_url: "https://arxiv.org/pdf/2402.01801.pdf"
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

# Time Series Foundation Models: A Comprehensive Survey

## 1. Verified Paper Identity & Links
- **Title**: Time Series Foundation Models: A Comprehensive Survey
- **Authors**: Jin et al.
- **arXiv Entry**: [https://arxiv.org/abs/2402.01801](https://arxiv.org/abs/2402.01801)
- **Full PDF**: [https://arxiv.org/pdf/2402.01801.pdf](https://arxiv.org/pdf/2402.01801.pdf)
- **Field**: ai_for_science

## 2. Official Paper Abstract
Large Language Models (LLMs) have seen significant use in domains such as natural language processing and computer vision. Going beyond text, image and graphics, LLMs present a significant potential for analysis of time series data, benefiting domains such as climate, IoT, healthcare, traffic, audio and finance. This survey paper provides an in-depth exploration and a detailed taxonomy of the various methodologies employed to harness the power of LLMs for time series analysis. We address the inherent challenge of bridging the gap between LLMs&#39; original text data training and the numerical nature of time series data, and explore strategies for transferring and distilling knowledge from LLMs to numerical time series analysis. We detail various methodologies, including (1) direct prompting of LLMs, (2) time series quantization, (3) aligning techniques, (4) utilization of the vision modality as a bridging mechanism, and (5) the combination of LLMs with tools. Additionally, this survey offers a comprehensive overview of the existing multimodal time series and text datasets and delves into the challenges and future opportunities of this emerging field. We maintain an up-to-date Github repository which includes all the papers and datasets discussed in the survey.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Scalability Bottlenecks in time-series-foundation-models)**: Computational and memory ceilings when scaling algorithms on high-dimensional inputs.

- **Challenge 2 (Generalization & Distribution Shifts in temporal-patching)**: Performance degradation when evaluated on out-of-distribution benchmarks and dynamic environments.

- **Challenge 3 (Evaluation Gaps & Alignment with cross-domain-forecasting)**: Disconnect between current proxy metrics and authentic downstream utility.

- **Challenge 4 (Theoretical Foundations of zero-shot-time-series)**: Establishing formal guarantees and provable bounds on convergence and stability.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
