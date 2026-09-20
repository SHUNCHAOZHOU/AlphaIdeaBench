# AlphaIdeaBench

LLM-as-judge code for scoring research ideas on **twelve dimensions**, and for turning **human peer-review comments** into the same scores so the judge can be aligned.

This repository is judge-only. It does not generate ideas.

## Twelve dimensions

| Group | Dimensions |
| --- | --- |
| Validity | Context grounding, Problem formulation, Motivation and method consistency, Testability |
| Novelty | Problem novelty, Method novelty, Scenario novelty, Insight novelty |
| Feasibility | Technical feasibility, Data feasibility, Budget feasibility, Verification feasibility |

Overall is the unweighted mean of these twelve scores. Each dimension is an independent judge call with its own rubric and checklist in `prompts/dimensions.yaml`.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

Set `OPENROUTER_API_KEY` in `.env`. The default chat model is in `configs/default.yaml`. Use `configs/gemini.yaml` for the native Gemini endpoint.

## 1. Score an idea (12 dimensions)

Dry run (no API):

```bash
alphaideabench list-dimensions
alphaideabench judge \
  --topic examples/topics/icbinb.md \
  --ideas examples/ideas/sample_idea.json \
  --repeats 1 --dry-run --skip-track2
```

Real judge:

```bash
alphaideabench judge \
  --topic examples/topics/icbinb.md \
  --ideas examples/ideas/sample_idea.json \
  --repeats 1 --skip-track2 --workers 12
```

`--ideas` can be one JSON file or a directory. The schema is documented below. Outputs go to `outputs/run_<timestamp>/`.

## 2. Map human review comments onto the same 12 dimensions

The mapper does **not** review the paper. It only reads what human reviewers already wrote and places that judgement on the rubric. Dimensions the reviews never mention come back as `covered: false` with a null score.

```bash
# inspect the prompt
python scripts/map_reviews_to_dimensions.py --limit 1 --print-prompt

# dry run on the bundled sample
python scripts/map_reviews_to_dimensions.py \
  --papers examples/reviews/sample_papers.json \
  --mode review --dry-run \
  --out outputs/review_mapping/sample
```

`--mode review` maps each review separately (keeps inter-reviewer spread). `--mode paper` maps all reviews of one paper in one call.

## 3. Align judge scores with the human mapping

After you have judge scores and human-mapped scores:

```bash
python scripts/align_judge_to_human.py \
  --judge examples/alignment/judge_scores.json \
  --human examples/alignment/human_scores.json
```

Reported metrics: DistAcc, MAD, within +/- 1, exact agreement, 3-class accuracy, Spearman rho. Uncovered human facets are skipped.

For the four novelty axes used in the paper meta-evaluation, the two-stage pipeline is:

```bash
# stage 1+2: extract quotes from reviews, then score only from those quotes
python scripts/novelty_reference.py \
  --papers examples/reviews/sample_papers.json \
  --dry-run --out outputs/novelty_reference/sample

# judge title+abstract only (reviews are never shown to the judge)
python scripts/judge_iclr_novelty.py \
  --papers examples/reviews/sample_papers.json \
  --reference outputs/novelty_reference/sample/papers.json \
  --topic examples/topics/icbinb.md \
  --dry-run --out outputs/judge_iclr_novelty/sample

# coverage of human quotes by judge reasoning (needs embeddings)
python scripts/compute_coverage_openai.py \
  --human outputs/novelty_reference/sample/records.jsonl \
  --judge outputs/judge_iclr_novelty/sample/records.jsonl
```

## Idea JSON

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

Only `title` is required. AI-Scientist-v2 ideation JSON (`Name` / `Title` / `Short Hypothesis` / ...) is also accepted.

## Topic markdown

The topic file is the judge's factual boundary. Novelty is scored against the prior work written here, not against a live web search. The YAML frontmatter must include a `budget` block.

See `examples/topics/icbinb.md`.

## Tests

```bash
pytest
```

## Layout

```
src/alphaideabench/   judge agent, 12-dimension rubric loader, Track 1/2
prompts/              judge and review-mapper prompts; dimensions.yaml
scripts/
  map_reviews_to_dimensions.py   human comments -> 12-dimension scores
  novelty_reference.py           extract quotes, then score novelty only
  judge_iclr_novelty.py          judge title+abstract; correlate vs reference
  align_judge_to_human.py        DistAcc / MAD / Spearman
  compute_coverage_openai.py     remark coverage via embeddings
examples/             topic, idea, sample reviews, alignment fixtures
```
