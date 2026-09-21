---
id: survey_25_video_understanding_reasoning
type: survey
field: multimodal_and_cv
title: "Video Understanding with Large Language Models: A Survey"
arxiv_id: "2312.17432"
authors: "Yolo Y. Tang, Jing Bi, Siting Xu et al."
source_url: "https://arxiv.org/abs/2312.17432"
pdf_url: "https://arxiv.org/pdf/2312.17432.pdf"
keywords:
  - video-understanding
  - long-video-reasoning
  - spatio-temporal-modeling
  - video-qa
  - token-compression
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---
# Video Understanding with Large Language Models: A Survey

## 1. Verified Paper Identity & Links
- **Title**: Video Understanding with Large Language Models: A Survey
- **Authors**: Yolo Y. Tang, Jing Bi, Siting Xu et al.
- **arXiv Entry**: [https://arxiv.org/abs/2312.17432](https://arxiv.org/abs/2312.17432)
- **Full PDF**: [https://arxiv.org/pdf/2312.17432.pdf](https://arxiv.org/pdf/2312.17432.pdf)
- **Field**: multimodal_and_cv

## 2. Official Paper Abstract
With the burgeoning growth of online video platforms and the escalating volume of video content, the demand for proficient video understanding tools has intensified markedly. Given the remarkable capabilities of large language models (LLMs) in language and multimodal tasks, this survey provides a detailed overview of recent advancements in video understanding that harness the power of LLMs (Vid-LLMs). The emergent capabilities of Vid-LLMs are surprisingly advanced, particularly their ability for open-ended multi-granularity (general, temporal, and spatiotemporal) reasoning combined with commonsense knowledge, suggesting a promising path for future video understanding. We examine the unique characteristics and capabilities of Vid-LLMs, categorizing the approaches into three main types: Video Analyzer x LLM, Video Embedder x LLM, and (Analyzer + Embedder) x LLM. Furthermore, we identify five sub-types based on the functions of LLMs in Vid-LLMs: LLM as Summarizer, LLM as Manager, LLM as Text Decoder, LLM as Regressor, and LLM as Hidden Layer. Furthermore, this survey presents a comprehensive study of the tasks, datasets, benchmarks, and evaluation methodologies for Vid-LLMs. Additionally, it explores the expansive applications of Vid-LLMs across various domains, highlighting their remarkable scalability and versatility in real-world video understanding challenges. Finally, it summarizes the limitations of existing Vid-LLMs and outlines directions for future research. For more information, readers are recommended to visit the repository at https://github.com/yunlong10/Awesome-LLMs-for-Video-Understanding.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Scalability Bottlenecks in video-understanding)**: Computational and memory ceilings when scaling algorithms on high-dimensional inputs.

- **Challenge 2 (Generalization & Distribution Shifts in long-video-reasoning)**: Performance degradation when evaluated on out-of-distribution benchmarks and dynamic environments.

- **Challenge 3 (Evaluation Gaps & Alignment with spatio-temporal-modeling)**: Disconnect between current proxy metrics and authentic downstream utility.

- **Challenge 4 (Theoretical Foundations of video-qa)**: Establishing formal guarantees and provable bounds on convergence and stability.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
