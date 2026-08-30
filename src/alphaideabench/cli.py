from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from alphaideabench.config import Settings
from alphaideabench.domain.dimensions import load_catalog
from alphaideabench.domain.topic import Topic
from alphaideabench.ideas_io import load_ideas
from alphaideabench.metrics import spearman_correlation
from alphaideabench.pipeline import BenchmarkPipeline, make_run_dir
from alphaideabench.tracks.track2 import build_embedder, evaluate_diversity

app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    help="AlphaIdeaBench CLI — 评价外部 idea agent 产出的 research idea。",
)
console = Console()


def _settings(config: Optional[Path]) -> Settings:
    return Settings.load(config)


@app.command("list-dimensions")
def list_dimensions() -> None:
    """列出 Track 1 的 13 个评分维度。"""
    catalog = load_catalog()
    table = Table(title="AlphaIdeaBench dimensions")
    table.add_column("#", justify="right")
    table.add_column("id")
    table.add_column("name")
    table.add_column("group")
    for dim in catalog.ordered():
        table.add_row(str(dim.index), dim.id, dim.name, dim.group)
    console.print(table)


@app.command()
def judge(
    topic: Path = typer.Option(..., exists=True, help="课题 markdown（需含 YAML frontmatter 与 budget）"),
    ideas: Path = typer.Option(
        ...,
        "--ideas",
        "--idea",
        exists=True,
        help="idea JSON，或包含若干 idea JSON 的目录。支持本仓库的 ResearchIdea 与 AI-Scientist-v2 格式",
    ),
    dimension: str = typer.Option("all", help="维度 id，或 all"),
    repeats: Optional[int] = typer.Option(None, help="每个维度重复打分次数（测一致性，默认 3）"),
    out: Path = typer.Option(Path("outputs"), help="输出根目录"),
    config: Optional[Path] = typer.Option(None, help="YAML 配置"),
    skip_track1: bool = typer.Option(False, help="跳过 13 维打分"),
    skip_track2: bool = typer.Option(False, help="跳过多样性"),
    dry_run: bool = typer.Option(False, help="使用 mock LLM，不调用真实 API"),
    workers: Optional[int] = typer.Option(
        None,
        help="Track 1 并行 worker 数（按维度并行；默认 1 串行，13 维可设 --workers 13）",
    ),
) -> None:
    """Track 1（13 维打分）+ Track 2（多样性）。目录内重复 idea 会去重。"""
    settings = _settings(config)
    t = Topic.from_markdown(topic)
    loaded = load_ideas(ideas, t)
    console.print(f"Loaded {len(loaded)} unique idea(s) from {ideas}")
    for idea in loaded:
        console.print(f"  - {idea.idea_id}: {idea.title}")

    catalog = load_catalog()
    dim_ids = None if dimension == "all" else [dimension]
    if dim_ids:
        unknown = [d for d in dim_ids if d not in catalog.dimensions]
        if unknown:
            raise typer.BadParameter(f"Unknown dimension: {unknown}")

    run_dir = make_run_dir(out)
    pipe = BenchmarkPipeline(settings, dry_run=dry_run)
    summary = pipe.judge_ideas(
        t,
        loaded,
        run_dir,
        repeats=repeats,
        skip_track1=skip_track1,
        skip_track2=skip_track2,
        dimension_ids=dim_ids,
        workers=workers,
    )
    for block in summary.get("track1") or []:
        _print_track1(block)
    t2 = summary.get("track2")
    if t2 and "mean_pairwise_similarity" in t2:
        console.print(
            f"Track2 mean_sim={t2['mean_pairwise_similarity']:.4f} "
            f"max_sim={t2['max_pairwise_similarity']:.4f}"
        )
    console.print(f"Run complete: {run_dir}")


app.command("judge-ideas", help="`judge` 的别名。")(judge)


@app.command()
def diversity(
    ideas_dir: Path = typer.Option(..., exists=True, help="存放 idea JSON 的目录"),
    topic: Path = typer.Option(..., exists=True, help="课题 markdown"),
    config: Optional[Path] = typer.Option(None),
    dry_run: bool = typer.Option(False),
) -> None:
    """只对一组 idea 计算 Track 2 多样性指标。"""
    settings = _settings(config)
    t = Topic.from_markdown(topic)
    loaded = load_ideas(ideas_dir, t)
    if len(loaded) < 2:
        raise typer.BadParameter("Need at least 2 ideas.")
    embedder = build_embedder(settings.embedding, dry_run=dry_run)
    metrics = evaluate_diversity(
        [i.embedding_text() for i in loaded], embedder, taus=settings.track2.taus
    )
    table = Table(title="Track 2 diversity")
    table.add_column("metric")
    table.add_column("value")
    table.add_row("n_ideas", str(metrics["n_ideas"]))
    table.add_row("mean_pairwise_similarity", f"{metrics['mean_pairwise_similarity']:.4f}")
    table.add_row("max_pairwise_similarity", f"{metrics['max_pairwise_similarity']:.4f}")
    table.add_row("semantic_diversity", f"{metrics['semantic_diversity']:.4f}")
    for tau, rate in metrics["duplicate_rate"].items():
        table.add_row(f"duplicate_rate@{tau}", f"{rate:.4f}")
    console.print(table)


@app.command()
def correlate(
    llm_scores: Path = typer.Option(..., exists=True, help="JSON list of {id, score}"),
    human_scores: Path = typer.Option(..., exists=True, help="JSON list of {id, score}"),
) -> None:
    """计算 LLM judge 与人工分数的 Spearman 相关（校准 judge prompt 用）。"""
    import json

    llm = {row["id"]: float(row["score"]) for row in json.loads(llm_scores.read_text(encoding="utf-8"))}
    human = {row["id"]: float(row["score"]) for row in json.loads(human_scores.read_text(encoding="utf-8"))}
    keys = sorted(set(llm) & set(human))
    if len(keys) < 2:
        raise typer.BadParameter("Need at least 2 overlapping ids.")
    rho = spearman_correlation([llm[k] for k in keys], [human[k] for k in keys])
    console.print(f"n={len(keys)}  Spearman ρ={rho:.4f}")


def _print_track1(payload: dict) -> None:
    table = Table(title=f"Track 1 · {payload.get('idea_id')}")
    table.add_column("dimension")
    table.add_column("mean")
    table.add_column("std")
    table.add_column("agreement")
    for dim_id, block in (payload.get("by_dimension") or {}).items():
        table.add_row(
            dim_id,
            f"{block['mean']:.2f}",
            f"{block['std']:.2f}",
            f"{block['exact_agreement']:.2f}",
        )
    console.print(table)
    groups = payload.get("group_means") or {}
    if groups:
        console.print("Group means: " + ", ".join(f"{k}={v:.2f}" for k, v in groups.items()))
