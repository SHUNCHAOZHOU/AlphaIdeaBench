---
id: survey_19_agentic_tool_use
type: survey
field: llm_and_reasoning
title: "Tool Learning with Large Language Models: A Survey"
arxiv_id: "2304.08354"
authors: "Changlei Chen, Yaobo Liang et al."
source_url: "https://arxiv.org/abs/2304.08354"
pdf_url: "https://arxiv.org/pdf/2304.08354.pdf"
keywords:
  - tool-use
  - function-calling
  - api-integration
  - argument-parsing
  - indirect-prompt-injection
budget:
  gpu: "4x A100 40GB (academic lab)"
  gpu_hours: 200
  calendar_weeks: 8
  api_usd: 200
  annotator_hours: 40
  notes: "Typical academic-lab compute & budget. Proposed solution must target one or more of the authentic open challenges identified in this survey paper, including official baselines and ablations." 
---

# Tool Learning with Large Language Models: A Survey

## 1. Verified Paper Identity & Links
- **Title**: Tool Learning with Large Language Models: A Survey
- **Authors**: Changlei Chen, Yaobo Liang et al.
- **arXiv Entry**: [https://arxiv.org/abs/2304.08354](https://arxiv.org/abs/2304.08354)
- **Full PDF**: [https://arxiv.org/pdf/2304.08354.pdf](https://arxiv.org/pdf/2304.08354.pdf)
- **Field**: llm_and_reasoning

## 2. Official Paper Abstract
Humans possess an extraordinary ability to create and utilize tools, allowing them to overcome physical limitations and explore new frontiers. With the advent of foundation models, AI systems have the potential to be equally adept in tool use as humans. This paradigm, i.e., tool learning with foundation models, combines the strengths of specialized tools and foundation models to achieve enhanced accuracy, efficiency, and automation in problem-solving. Despite its immense potential, there is still a lack of a comprehensive understanding of key challenges, opportunities, and future endeavors in this field. To this end, we present a systematic investigation of tool learning in this paper. We first introduce the background of tool learning, including its cognitive origins, the paradigm shift of foundation models, and the complementary roles of tools and models. Then we recapitulate existing tool learning research into tool-augmented and tool-oriented learning. We formulate a general tool learning framework: starting from understanding the user instruction, models should learn to decompose a complex task into several subtasks, dynamically adjust their plan through reasoning, and effectively conquer each sub-task by selecting appropriate tools. We also discuss how to train models for improved tool-use capabilities and facilitate the generalization in tool learning. Considering the lack of a systematic tool learning evaluation in prior works, we experiment with 18 representative tools and show the potential of current foundation models in skillfully utilizing tools. Finally, we discuss several open problems that require further investigation for tool learning. In general, we hope this paper could inspire future research in integrating tools with foundation models.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Large-Scale Tool Retrieval and Selection)**: Selecting the correct API among thousands of candidates when documentation exceeds context length limits.

- **Challenge 2 (Complex Schema & Parameter Compliance)**: Generating deeply nested JSON structures or binary payloads frequently triggers runtime schema validation exceptions.

- **Challenge 3 (Indirect Tool Output Prompt Injection)**: Malicious data retrieved from external APIs hijacks agent instructions and executes unauthorized actions.

- **Challenge 4 (Concurrent & Asynchronous Tool Orchestration)**: Agents lack native mechanisms to coordinate and join concurrent asynchronous API calls.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
