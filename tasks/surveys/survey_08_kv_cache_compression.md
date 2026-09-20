---
id: survey_08_kv_cache_compression
type: survey
field: efficiency_and_systems
title: "SoK: Key-Value Cache Compression for Large Language Models"
arxiv_id: "2407.18003"
authors: "Yuan Zhang et al."
source_url: "https://arxiv.org/abs/2407.18003"
pdf_url: "https://arxiv.org/pdf/2407.18003.pdf"
keywords:
  - kv-cache-compression
  - long-context-serving
  - token-eviction
  - quantization
  - sparse-attention
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---

# SoK: Key-Value Cache Compression for Large Language Models

## 1. Verified Paper Identity & Links
- **Title**: SoK: Key-Value Cache Compression for Large Language Models
- **Authors**: Yuan Zhang et al.
- **arXiv Entry**: [https://arxiv.org/abs/2407.18003](https://arxiv.org/abs/2407.18003)
- **Full PDF**: [https://arxiv.org/pdf/2407.18003.pdf](https://arxiv.org/pdf/2407.18003.pdf)
- **Field**: efficiency_and_systems

## 2. Official Paper Abstract
Large Language Models (LLMs), epitomized by ChatGPT&#39;s release in late 2022, have revolutionized various industries with their advanced language comprehension. However, their efficiency is challenged by the Transformer architecture&#39;s struggle with handling long texts. KV Cache has emerged as a pivotal solution to this issue, converting the time complexity of token generation from quadratic to linear, albeit with increased GPU memory overhead proportional to conversation length. With the development of the LLM community and academia, various KV Cache compression methods have been proposed. In this review, we dissect the various properties of KV Cache and elaborate on various methods currently used to optimize the KV Cache space usage of LLMs. These methods span the pre-training phase, deployment phase, and inference phase, and we summarize the commonalities and differences among these methods. Additionally, we list some metrics for evaluating the long-text capabilities of large language models, from both efficiency and capability perspectives. Our review thus sheds light on the evolving landscape of LLM optimization, offering insights into future advancements in this dynamic field. Links to the papers mentioned in this review can be found in our Github Repo <a href="https://github.com/zcli-charlie/Awesome-KV-Cache" rel="external noopener nofollow" class="link-external link-https">this https URL</a>.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Needle-in-a-Haystack Token Eviction Pathology)**: Cumulative attention heuristics inadvertently discard dormant tokens essential for late-stage queries.

- **Challenge 2 (Extreme Low-Bit Precision Loss in Attention Matrices)**: Sub-3-bit quantization of keys and values triggers severe attention distortion and perplexity explosion.

- **Challenge 3 (Dynamic Context Page Rehydration)**: Inability to re-fetch or reconstruct evicted KV cache pages when conversation context abruptly switches to past topics.

- **Challenge 4 (Hardware Memory Coalescing on Sparse KV Layouts)**: Non-contiguous sparse memory access patterns fail to achieve theoretical compute speedups on GPU Tensor Cores.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
