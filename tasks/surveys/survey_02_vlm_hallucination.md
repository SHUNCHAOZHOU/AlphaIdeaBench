---
id: survey_02_vlm_hallucination
type: survey
field: multimodal_and_cv
title: "A Survey on Hallucination in Large Vision-Language Models"
arxiv_id: "2402.00253"
authors: "Hao Liu et al."
source_url: "https://arxiv.org/abs/2402.00253"
pdf_url: "https://arxiv.org/pdf/2402.00253.pdf"
keywords:
  - vlm-hallucination
  - object-existence
  - attribute-binding
  - visual-faithfulness
  - cross-attention-bias
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---

# A Survey on Hallucination in Large Vision-Language Models

## 1. Verified Paper Identity & Links
- **Title**: A Survey on Hallucination in Large Vision-Language Models
- **Authors**: Hao Liu et al.
- **arXiv Entry**: [https://arxiv.org/abs/2402.00253](https://arxiv.org/abs/2402.00253)
- **Full PDF**: [https://arxiv.org/pdf/2402.00253.pdf](https://arxiv.org/pdf/2402.00253.pdf)
- **Field**: multimodal_and_cv

## 2. Official Paper Abstract
Recent development of Large Vision-Language Models (LVLMs) has attracted growing attention within the AI landscape for its practical implementation potential. However, ``hallucination&#39;&#39;, or more specifically, the misalignment between factual visual content and corresponding textual generation, poses a significant challenge of utilizing LVLMs. In this comprehensive survey, we dissect LVLM-related hallucinations in an attempt to establish an overview and facilitate future mitigation. Our scrutiny starts with a clarification of the concept of hallucinations in LVLMs, presenting a variety of hallucination symptoms and highlighting the unique challenges inherent in LVLM hallucinations. Subsequently, we outline the benchmarks and methodologies tailored specifically for evaluating hallucinations unique to LVLMs. Additionally, we delve into an investigation of the root causes of these hallucinations, encompassing insights from the training data and model components. We also critically review existing methods for mitigating hallucinations. The open questions and future directions pertaining to hallucinations within LVLMs are discussed to conclude this survey.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Statistical Language Prior Dominance)**: Decoders over-rely on unimodal text co-occurrence statistics, predicting common visual patterns regardless of actual image pixel content.

- **Challenge 2 (Visual Token Dilution & Resolution Bottlenecks)**: Downsampling high-resolution images strips dense fine-grained spatial and text details, causing misattribution in cluttered scenes.

- **Challenge 3 (Fine-Grained Attribute-Object Misbinding)**: Inability of shallow cross-attention layers to correctly associate colors, materials, and relative positions with respective instances.

- **Challenge 4 (Evaluation Gaming via Output Length & Yes/No Biases)**: Binary classification benchmarks (POPE) fail to detect nuanced multi-sentence descriptive hallucinations.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
