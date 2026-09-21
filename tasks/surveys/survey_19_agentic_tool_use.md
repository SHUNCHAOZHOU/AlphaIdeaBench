---
id: survey_19_agentic_tool_use
type: survey
field: llm_and_reasoning
title: "Tool Learning with Large Language Models: A Survey"
arxiv_id: "2405.17935"
authors: "Changle Qu, Sunhao Dai, Xiaochi Wei et al."
source_url: "https://arxiv.org/abs/2405.17935"
pdf_url: "https://arxiv.org/pdf/2405.17935.pdf"
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
- **Authors**: Changle Qu, Sunhao Dai, Xiaochi Wei et al.
- **arXiv Entry**: [https://arxiv.org/abs/2405.17935](https://arxiv.org/abs/2405.17935)
- **Full PDF**: [https://arxiv.org/pdf/2405.17935.pdf](https://arxiv.org/pdf/2405.17935.pdf)
- **Field**: llm_and_reasoning

## 2. Official Paper Abstract
Recently, tool learning with large language models (LLMs) has emerged as a promising paradigm for augmenting the capabilities of LLMs to tackle highly complex problems. Despite growing attention and rapid advancements in this field, the existing literature remains fragmented and lacks systematic organization, posing barriers to entry for newcomers. This gap motivates us to conduct a comprehensive survey of existing works on tool learning with LLMs. In this survey, we focus on reviewing existing literature from the two primary aspects (1) why tool learning is beneficial and (2) how tool learning is implemented, enabling a comprehensive understanding of tool learning with LLMs. We first explore the "why" by reviewing both the benefits of tool integration and the inherent benefits of the tool learning paradigm from six specific aspects. In terms of "how", we systematically review the literature according to a taxonomy of four key stages in the tool learning workflow: task planning, tool selection, tool calling, and response generation. Additionally, we provide a detailed summary of existing benchmarks and evaluation methods, categorizing them according to their relevance to different stages. Finally, we discuss current challenges and outline potential future directions, aiming to inspire both researchers and industrial developers to further explore this emerging and promising area. We also maintain a GitHub repository to continually keep track of the relevant papers and resources in this rising area at https://github.com/quchangle1/LLM-Tool-Survey.

## 3. Explicit Research Gaps & Open Challenges
The following core challenges and research gaps are extracted and synthesized directly from the survey's *Open Problems / Challenges / Future Work* sections:

- **Challenge 1 (Large-Scale Tool Retrieval and Selection)**: Selecting the correct API among thousands of candidates when documentation exceeds context length limits.

- **Challenge 2 (Complex Schema & Parameter Compliance)**: Generating deeply nested JSON structures or binary payloads frequently triggers runtime schema validation exceptions.

- **Challenge 3 (Indirect Tool Output Prompt Injection)**: Malicious data retrieved from external APIs hijacks agent instructions and executes unauthorized actions.

- **Challenge 4 (Concurrent & Asynchronous Tool Orchestration)**: Agents lack native mechanisms to coordinate and join concurrent asynchronous API calls.

## 4. Evaluation Scope & Constraints
Auto Research Agents must formulate an innovative, testable research proposal aimed at resolving at least one of the explicit challenges above. The proposed methodology and experiments must fit within standard academic computing budgets (e.g. 4x A100 GPU cluster, 200 GPU-hours) using publicly accessible datasets and models.
