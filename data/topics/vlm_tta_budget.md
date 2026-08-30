---
id: vlm-tta-budget
field: computer_vision
title: Test-time adaptation for vision-language models under a small compute budget
keywords:
  - vision-language models
  - test-time adaptation
  - CLIP
  - distribution shift
budget:
  gpu: "1x RTX 4090 24GB"
  gpu_hours: 40
  calendar_weeks: 4
  api_usd: 0
  annotator_hours: 0
  notes: "Public data only. No paid APIs, no extra labels, no multi-GPU. A meaningful evaluation must include official baselines, at least one ablation, and 3 random seeds on the public shifts listed below."
---

# Research background

Vision-language models such as CLIP (Radford et al., 2021) show strong zero-shot transfer, but accuracy drops under distribution shift (ImageNet-A/R/V2, rendition, sketches, and other natural shifts). A practical question for small labs is: **can we adapt a frozen CLIP-like model at test time without labeled target data and without large-scale retraining?**

## Related work and limitations

- **CLIP** (Radford et al., 2021) provides a frozen image encoder + text encoder and a prompt-based zero-shot classifier. It does not adapt to a target stream.
- **CoOp / CoCoOp** (Zhou et al., 2022) learn continuous prompts, but they need **source labeled data and a training stage**. They are not test-time methods and exceed the budget if retrained at ImageNet scale.
- **TENT** (Wang et al., 2021) adapts batch-norm statistics by entropy minimization. It assumes BN layers and mini-batches; many ViT-based CLIP encoders do not fit this recipe cleanly.
- **TPT** (Shu et al., 2022, NeurIPS) performs test-time prompt tuning with confidence selection on augmented views of **a single test image**. It is the closest prior in this topic. Limitations called out in follow-up work: per-image optimization is slow, prompts can overfit a single image, and gains vary widely across shifts.
- **TDA / training-free caches** (e.g. Karmanov et al., 2024 and related cache-based adapters) avoid gradient updates by storing confident pseudo-labeled features. Limitations: cache quality depends on the confidence rule; they may not help on severe shifts; hyper-parameters are often tuned on the test distribution.

## Open problems in this topic

1. Adaptation that is **both cheap enough for a 4090 / 40 GPU-hour budget** and stronger than TPT/TDA on public shifts.
2. When test-time adaptation **hurts** rather than helps (negative transfer), and how to detect that without labels.
3. Whether the bottleneck is the prompt, the visual features, the confidence filter, or the lack of a reliable stop criterion.
4. Evaluation that reports wall-clock cost per image, not only accuracy.

## Allowed evaluation setting

- Backbones: public CLIP ViT-B/16 or ViT-B/32 checkpoints only.
- Datasets: ImageNet validation plus public shifts ImageNet-A, ImageNet-R, ImageNet-V2. Subsampling is allowed if the protocol is fixed in advance and applied to all methods.
- Baselines that must be included if claimed as competitors: zero-shot CLIP, TPT, and one training-free cache/adapter.
- No ImageNet full training, no extra human labels, no private test data.

## Out of scope

Pretraining a new VLM, RLHF-style annotation, or any method whose meaningful verification needs more than 40 GPU hours.
