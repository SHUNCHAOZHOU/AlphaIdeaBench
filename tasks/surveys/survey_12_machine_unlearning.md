---
id: survey_12_machine_unlearning
type: survey
field: trustworthy_and_safety
title: "A Survey of Machine Unlearning"
arxiv_id: "2209.02299"
authors: "Thanh Tam Nguyen, Thanh Trung Huynh, Zhao Ren et al."
source_url: "https://arxiv.org/abs/2209.02299"
pdf_url: "https://arxiv.org/pdf/2209.02299.pdf"
keywords:
  - machine-unlearning
  - privacy-preservation
  - copyright-scrubbing
  - gradient-inversion
  - forget-quality
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---
# A Survey of Machine Unlearning

## 1. Verified Paper Identity & Links
- **Title**: A Survey of Machine Unlearning
- **Authors**: Thanh Tam Nguyen, Thanh Trung Huynh, Zhao Ren et al.
- **arXiv Entry**: [https://arxiv.org/abs/2209.02299](https://arxiv.org/abs/2209.02299)
- **Full PDF**: [https://arxiv.org/pdf/2209.02299.pdf](https://arxiv.org/pdf/2209.02299.pdf)
- **Field**: trustworthy_and_safety

## 2. Official Paper Abstract
Today, computer systems hold large amounts of personal data. Yet while such an abundance of data allows breakthroughs in artificial intelligence, and especially machine learning (ML), its existence can be a threat to user privacy, and it can weaken the bonds of trust between humans and AI. Recent regulations now require that, on request, private information about a user must be removed from both computer systems and from ML models, i.e. ``the right to be forgotten''). While removing data from back-end databases should be straightforward, it is not sufficient in the AI context as ML models often `remember' the old data. Contemporary adversarial attacks on trained models have proven that we can learn whether an instance or an attribute belonged to the training data. This phenomenon calls for a new paradigm, namely machine unlearning, to make ML models forget about particular data. It turns out that recent works on machine unlearning have not been able to completely solve the problem due to the lack of common frameworks and resources. Therefore, this paper aspires to present a comprehensive examination of machine unlearning's concepts, scenarios, methods, and applications. Specifically, as a category collection of cutting-edge studies, the intention behind this article is to serve as a comprehensive resource for researchers and practitioners seeking an introduction to machine unlearning and its formulations, design criteria, removal requests, algorithms, and applications. In addition, we aim to highlight the key findings, current trends, and new research areas that have not yet featured the use of machine unlearning but could benefit greatly from it. We hope this survey serves as a valuable resource for ML researchers and those seeking to innovate privacy technologies. Our resources are publicly available at https://github.com/tamlhp/awesome-machine-unlearning.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Residual Memorization Extraction)**: Approximate unlearning only alters top-layer outputs, leaving latent representations extractable via adversarial prompts.

- **Challenge 2 (Collateral Damage to Adjacent Knowledge)**: Erasing specific private or copyrighted entities degrades knowledge of related, harmless concepts.

- **Challenge 3 (Lack of Certified Unlearning Guarantees)**: In non-convex multi-billion parameter networks, verifying that a sample was mathematically erased remains unproven.

- **Challenge 4 (Scalability vs Retraining Feasibility)**: Existing exact unlearning methods incur computational costs comparable to retraining from scratch.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
