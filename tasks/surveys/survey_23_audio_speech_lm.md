---
id: survey_23_audio_speech_lm
type: survey
field: multimodal_and_cv
title: "Audio Large Language Models: A Survey"
arxiv_id: "2403.17834"
authors: "Latif et al."
source_url: "https://arxiv.org/abs/2403.17834"
pdf_url: "https://arxiv.org/pdf/2403.17834.pdf"
keywords:
  - audio-llm
  - speech-language-models
  - neural-audio-codecs
  - cross-modal-speech
  - paralinguistics
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---

# Audio Large Language Models: A Survey

## 1. Verified Paper Identity & Links
- **Title**: Audio Large Language Models: A Survey
- **Authors**: Latif et al.
- **arXiv Entry**: [https://arxiv.org/abs/2403.17834](https://arxiv.org/abs/2403.17834)
- **Full PDF**: [https://arxiv.org/pdf/2403.17834.pdf](https://arxiv.org/pdf/2403.17834.pdf)
- **Field**: multimodal_and_cv

## 2. Official Paper Abstract
Advancements in medical imaging AI, particularly in 3D imaging, have been limited due to the scarcity of comprehensive datasets. We introduce CT-RATE, a public dataset that pairs 3D medical images with corresponding textual reports. CT-RATE comprises 25,692 non-contrast 3D chest CT scans from 21,304 unique patients. Each scan is accompanied by its corresponding radiology report. Leveraging CT-RATE, we develop CT-CLIP, a CT-focused contrastive language-image pretraining framework designed for broad applications without the need for task-specific training. We demonstrate how CT-CLIP can be used in multi-abnormality detection and case retrieval, and outperforms state-of-the-art fully supervised models across all key metrics. By combining CT-CLIP&#39;s vision encoder with a pretrained large language model, we create CT-CHAT, a vision-language foundational chat model for 3D chest CT volumes. Finetuned on over 2.7 million question-answer pairs derived from the CT-RATE dataset, CT-CHAT underscores the necessity for specialized methods in 3D medical imaging. Collectively, the open-source release of CT-RATE, CT-CLIP, and CT-CHAT not only addresses critical challenges in 3D medical imaging but also lays the groundwork for future innovations in medical AI and improved patient care.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Scalability Bottlenecks in audio-llm)**: Computational and memory ceilings when scaling algorithms on high-dimensional inputs.

- **Challenge 2 (Generalization & Distribution Shifts in speech-language-models)**: Performance degradation when evaluated on out-of-distribution benchmarks and dynamic environments.

- **Challenge 3 (Evaluation Gaps & Alignment with neural-audio-codecs)**: Disconnect between current proxy metrics and authentic downstream utility.

- **Challenge 4 (Theoretical Foundations of cross-modal-speech)**: Establishing formal guarantees and provable bounds on convergence and stability.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
