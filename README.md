# AlphaIdeaBench

把「这个 research idea 好不好」拆成一组可独立测量的细粒度维度，用 **通用 Agent 框架**（LLM + prompt + tool）做 LLM-as-Judge 评审，并显式纳入 **Feasibility / Budget**。

**本仓库只做评价，不生成 idea。** idea 来自被测的外部 idea agent（AI-Scientist-v2、你自己的 agent、人写的提案都行）。Budget 写在课题文档里，作为评审的硬约束——被测 agent 也应该看到同一份预算，否则 Budget Feasibility 会失去区分度。

## 两个 Track

**Track 1 · 单 idea 质量（1–5 分）**

| 组 | 维度 |
| --- | --- |
| Validity | Context Grounding · Problem Formulation · Motivation–Method Consistency · Testability |
| Novelty | Problem / Method / Scenario / Insight Novelty |
| Feasibility | Technical / Data / Budget / Verification Feasibility |
| Readiness | Research Readiness（独立整体判断，不是其他分数的平均） |

打分：每个维度一个独立的 judge agent，prompt 内嵌评分表 + checklist，输出 reasoning + 分数；默认每维重复 3 次并报告一致性。

**Track 2 · 多样性（同一课题下的多个 idea）**

用 **Gemini Embedding 2**（OpenRouter slug：`google/gemini-embedding-2`）对完整 idea 文本编码，计算两两 cosine similarity：

- Mean Pairwise Similarity
- Max Pairwise Similarity（避免均值掩盖单点重复）
- Duplicate Rate（阈值 τ，默认报告 0.85 与 0.90）

Novelty 相对 **课题 context 中的已有工作** 判断，而不是实时检索全网文献，以保证同一条 idea 重复评审的分数可比。Judge 不联网。

## 架构

```
Agent = LLM backend + system/user prompt + 一组 tools + JSON 输出
        ↑ 通用循环（tool call → 执行 → 再问模型）
        │
        └── dimension_judge  prompts/judge_*.md   load_topic, load_budget, load_idea, load_rubric
```

13 个维度是同一个 judge 类的 13 次实例化，互不通信、不传分。换一个评审维度 = 改 `prompts/dimensions.yaml` 里的 rubric，代码不动。

```
src/alphaideabench/
  core/          通用 Agent、LLM、Tool registry、prompt 渲染
  domain/        Idea / Topic / 13 维 rubric / 分数
  agents/        DimensionJudge（薄封装）
  tools/         内置 tools
  tracks/        Track 1 重复打分、Track 2 embedding 多样性
  ideas_io.py    读取外部 idea agent 的产出并归一成 ResearchIdea
  pipeline.py    端到端跑数
  cli.py         命令行
prompts/         人工撰写的 prompt 与维度评分表
data/topics/     课题 markdown（YAML frontmatter 里必须有 budget）
baseline/        被测的外部 idea agent（如 AI-Scientist-v2），不属于框架
```

## 安装

```bash
cd AlphaIdeaBench
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env   # 填入 API key
```

环境变量（默认全部走 [OpenRouter](https://openrouter.ai/)）：

| 变量 | 用途 |
| --- | --- |
| `OPENROUTER_API_KEY` | Judge 的 chat 与 Track 2 的 `google/gemini-embedding-2` |
| `model` 或 `OPENROUTER_MODEL` | Chat 模型 slug，覆盖 YAML 里的 `llm.model` |
| `JUDGE_MODEL` | 可选，只覆盖 Judge |
| `EMBEDDING_MODEL` | 可选，覆盖 Track 2 embedding（默认不要改） |
| `ALPHAIDEABENCH_ROOT` | 可选，指向仓库根目录（找不到 `prompts/dimensions.yaml` 时设置） |

`.env` 里的 `model=...` 只改 **chat 模型**，不会改 embedding：

```bash
OPENROUTER_API_KEY=sk-or-v1-...
model=deepseek/deepseek-v4-flash-0731
```

也可以在 `configs/default.yaml` 里写：

```yaml
llm:
  provider: openrouter
  model: deepseek/deepseek-v4-flash-0731
  api_key_env: OPENROUTER_API_KEY
  base_url: https://openrouter.ai/api/v1

embedding:
  provider: openrouter
  model: google/gemini-embedding-2

agents:
  judge:
    model: anthropic/claude-sonnet-4      # 可选：Judge 用更强模型
```

## 快速开始

不调真实 API 的冒烟（mock LLM + mock embedding）：

```bash
alphaideabench list-dimensions
alphaideabench judge --topic data/topics/icbinb.md \
  --ideas baseline/AI-Scientist-v2/ai_scientist/ideas --repeats 1 --dry-run
```

真实评测。`--ideas` 可以是单个 JSON，也可以是一个目录；重复的 idea 会去重：

```bash
# 小规模：每维打 1 次（建议先跑这个）
alphaideabench judge --topic data/topics/icbinb.md \
  --ideas baseline/AI-Scientist-v2/ai_scientist/ideas --repeats 1

# 完整：每维 3 次，测一致性
alphaideabench judge --topic data/topics/icbinb.md \
  --ideas baseline/AI-Scientist-v2/ai_scientist/ideas --repeats 3
```

`--repeats` 是同一维重复打分测一致性，**不是失败重试**。试跑请显式用 `--repeats 1`。13 个维度互不通信，可用 `--workers 13` 并行打分。

只跑一个维度（调 prompt 时很有用）：

```bash
alphaideabench judge --topic data/topics/fintech_credit_shift.md \
  --ideas outputs/.../ideas/xxx.json --dimension data_feasibility --repeats 1
```

只算多样性：

```bash
alphaideabench diversity --topic data/topics/icbinb.md --ideas-dir outputs/.../ideas
```

Judge 与人工分的 Spearman（JSON 均为 `[{id, score}, ...]`）：

```bash
alphaideabench correlate --llm-scores llm.json --human-scores human.json
```

## idea 输入格式

`--ideas` 支持两种 JSON（单个对象或对象数组，目录里混放也行）：

**1. 本仓库的 `ResearchIdea`**（字段见 `src/alphaideabench/domain/idea.py`）：

```json
{
  "idea_id": "my-topic-01",
  "title": "...",
  "research_question": "...",
  "problem": "...",
  "motivation": "...",
  "method": "...",
  "experiments": "...",
  "baselines": "...",
  "success_criteria": "...",
  "related_work": "...",
  "limitations": "...",
  "resource_plan": {"gpu": "1x RTX 4090 24GB", "estimated_gpu_hours": 30}
}
```

只有 `title` 是必填，其余缺失会按维度规则压分（例如 `baselines` 为空会拉低 Verification Feasibility）。

**2. AI-Scientist-v2 的 ideation JSON**（`Name` / `Title` / `Short Hypothesis` / `Related Work` / `Abstract` / `Experiments` / `Risk Factors and Limitations`）。会被映射成 `ResearchIdea`，并按 `Name` 去重；由于该格式没有结构化资源计划，`resource_plan` 用课题 budget 填充。

要接入新的 idea agent，把它的产出导成上面任一种 JSON 即可，不需要改框架。

## 如何写课题（必须含 Budget）

```markdown
---
id: my-topic
field: nlp
title: ...
keywords: [a, b]
budget:
  gpu: "1x RTX 4090 24GB"
  gpu_hours: 40
  calendar_weeks: 4
  api_usd: 0
  annotator_hours: 0
  notes: "Public data only. Must include baselines + ablation within budget."
---

# Research background
...
## Related work and limitations
...
## Open problems
...
```

课题文档是 Judge 的事实边界：Novelty 相对这里列出的已有工作判断，数据可行性也优先对照这里允许 / 禁止的数据源。把可用的公开数据集、禁止的私有数据写清楚，比让 Judge 去猜更可复现。

示例课题：`data/topics/vlm_tta_budget.md`、`data/topics/llm_sci_faithfulness.md`、`data/topics/icbinb.md`、`data/topics/fintech_credit_shift.md`。

## 如何改评分维度

编辑 `prompts/dimensions.yaml`（评分表 + checklist）。Judge 的 system prompt 会把当前维度的 rubric 嵌进去。不要把 13 个维度揉成一次打分：每个维度是一次独立 agent 调用。

`prompts/` 下所有喂给模型的文本（judge system / user prompt、13 维 rubric 与 checklist）统一用英文，和课题文档、idea 保持同一语言；新增维度时也请写英文。

自定义 tool：

```python
from alphaideabench.core.tools import tool, RunContext

@tool
def lookup_lab_constraint(ctx: RunContext) -> str:
    """Return local lab constraints beyond the topic budget."""
    return "No cloud GPUs."
```

然后把 `lookup_lab_constraint` 写进 `configs/default.yaml` 的 `agents.judge.tools`。

## 输出

每次 `judge` 写入 `outputs/run_<timestamp>/`：

- `config.json` — 复现用配置
- `<topic_id>/topic.json` 与 `<topic_id>/ideas/*.json` — 本次评的课题与 idea 快照
- `<topic_id>/track1/<idea_id>/<dimension>/repeat_*.json` — 含 reasoning、checklist 与完整对话
- `<topic_id>/track1/<idea_id>/aggregate.json` — 各维 mean / std / exact agreement，以及分组均分
- `<topic_id>/track2.json` — Mean/Max similarity 与各 τ 下 duplicate rate
- `<topic_id>/summary.json` — 汇总

## 测试

```bash
pytest
```
