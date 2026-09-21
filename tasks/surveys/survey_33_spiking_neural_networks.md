---
id: survey_33_spiking_neural_networks
type: survey
field: efficiency_and_systems
title: "Training Spiking Neural Networks Using Lessons From Deep Learning"
arxiv_id: "2109.12894"
authors: "Jason K. Eshraghian, Max Ward, Emre Neftci et al."
source_url: "https://arxiv.org/abs/2109.12894"
pdf_url: "https://arxiv.org/pdf/2109.12894.pdf"
keywords:
  - spiking-neural-networks
  - neuromorphic-computing
  - surrogate-gradients
  - event-driven-processing
  - energy-efficiency
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---
# Training Spiking Neural Networks Using Lessons From Deep Learning

## 1. Verified Paper Identity & Links
- **Title**: Training Spiking Neural Networks Using Lessons From Deep Learning
- **Authors**: Jason K. Eshraghian, Max Ward, Emre Neftci et al.
- **arXiv Entry**: [https://arxiv.org/abs/2109.12894](https://arxiv.org/abs/2109.12894)
- **Full PDF**: [https://arxiv.org/pdf/2109.12894.pdf](https://arxiv.org/pdf/2109.12894.pdf)
- **Field**: efficiency_and_systems

## 2. Official Paper Abstract
The brain is the perfect place to look for inspiration to develop more efficient neural networks. The inner workings of our synapses and neurons provide a glimpse at what the future of deep learning might look like. This paper serves as a tutorial and perspective showing how to apply the lessons learnt from several decades of research in deep learning, gradient descent, backpropagation and neuroscience to biologically plausible spiking neural neural networks. We also explore the delicate interplay between encoding data as spikes and the learning process; the challenges and solutions of applying gradient-based learning to spiking neural networks (SNNs); the subtle link between temporal backpropagation and spike timing dependent plasticity, and how deep learning might move towards biologically plausible online learning. Some ideas are well accepted and commonly used amongst the neuromorphic engineering community, while others are presented or justified for the first time here. The fields of deep learning and spiking neural networks evolve very rapidly. We endeavour to treat this document as a 'dynamic' manuscript that will continue to be updated as the common practices in training SNNs also change. A series of companion interactive tutorials complementary to this paper using our Python package, snnTorch, are also made available. See https://snntorch.readthedocs.io/en/latest/tutorials/index.html .

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Scalability Bottlenecks in spiking-neural-networks)**: Computational and memory ceilings when scaling algorithms on high-dimensional inputs.

- **Challenge 2 (Generalization & Distribution Shifts in neuromorphic-computing)**: Performance degradation when evaluated on out-of-distribution benchmarks and dynamic environments.

- **Challenge 3 (Evaluation Gaps & Alignment with surrogate-gradients)**: Disconnect between current proxy metrics and authentic downstream utility.

- **Challenge 4 (Theoretical Foundations of event-driven-processing)**: Establishing formal guarantees and provable bounds on convergence and stability.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
