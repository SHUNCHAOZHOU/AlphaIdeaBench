---
id: survey_17_peft_lora_adapters
type: survey
field: efficiency_and_systems
title: "Delta Tuning: A Comprehensive Study of Parameter Efficient Methods for Pre-trained Language Models"
arxiv_id: "2203.06904"
authors: "Ning Ding, Yujia Qin, Guang Yang et al."
source_url: "https://arxiv.org/abs/2203.06904"
pdf_url: "https://arxiv.org/pdf/2203.06904.pdf"
keywords:
  - peft
  - lora
  - delta-tuning
  - adapter-routing
  - low-rank-adaptation
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---
# Delta Tuning: A Comprehensive Study of Parameter Efficient Methods for Pre-trained Language Models

## 1. Verified Paper Identity & Links
- **Title**: Delta Tuning: A Comprehensive Study of Parameter Efficient Methods for Pre-trained Language Models
- **Authors**: Ning Ding, Yujia Qin, Guang Yang et al.
- **arXiv Entry**: [https://arxiv.org/abs/2203.06904](https://arxiv.org/abs/2203.06904)
- **Full PDF**: [https://arxiv.org/pdf/2203.06904.pdf](https://arxiv.org/pdf/2203.06904.pdf)
- **Field**: efficiency_and_systems

## 2. Official Paper Abstract
Despite the success, the process of fine-tuning large-scale PLMs brings prohibitive adaptation costs. In fact, fine-tuning all the parameters of a colossal model and retaining separate instances for different tasks are practically infeasible. This necessitates a new branch of research focusing on the parameter-efficient adaptation of PLMs, dubbed as delta tuning in this paper. In contrast with the standard fine-tuning, delta tuning only fine-tunes a small portion of the model parameters while keeping the rest untouched, largely reducing both the computation and storage costs. Recent studies have demonstrated that a series of delta tuning methods with distinct tuned parameter selection could achieve performance on a par with full-parameter fine-tuning, suggesting a new promising way of stimulating large-scale PLMs. In this paper, we first formally describe the problem of delta tuning and then comprehensively review recent delta tuning approaches. We also propose a unified categorization criterion that divide existing delta tuning methods into three groups: addition-based, specification-based, and reparameterization-based methods. Though initially proposed as an efficient method to steer large models, we believe that some of the fascinating evidence discovered along with delta tuning could help further reveal the mechanisms of PLMs and even deep neural networks. To this end, we discuss the theoretical principles underlying the effectiveness of delta tuning and propose frameworks to interpret delta tuning from the perspective of optimization and optimal control, respectively. Furthermore, we provide a holistic empirical study of representative methods, where results on over 100 NLP tasks demonstrate a comprehensive performance comparison of different approaches. The experimental results also cover the analysis of combinatorial, scaling and transferable properties of delta tuning.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Destructive Interference in Multi-Adapter Merging)**: Linearly combining weights of independently trained LoRA adapters degrades performance across all tasks.

- **Challenge 2 (Uniform Rank Allocation Inefficiency)**: Assigning fixed ranks across all layers wastes parameters on invariant layers while starving expressive layers.

- **Challenge 3 (Quantization-Aware Gradient Mismatch)**: Fine-tuning low-rank adapters over 4-bit quantized backbones introduces gradient calculation errors.

- **Challenge 4 (Theoretical Capacity Bounds of Low-Rank Matrices)**: Lack of formal bounds establishing which tasks exceed the expressive capacity of rank-r updates.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
