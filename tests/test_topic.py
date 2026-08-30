from alphaideabench.domain.topic import Topic


def test_topic_frontmatter_and_budget(tmp_path):
    path = tmp_path / "demo.md"
    path.write_text(
        """---
id: demo-1
field: nlp
title: Demo topic
keywords: [a, b]
budget:
  gpu: "1x A100"
  gpu_hours: 10
  calendar_weeks: 2
  api_usd: 5
  annotator_hours: 1
  notes: "public data only"
---

# Background

A gap remains in X.
""",
        encoding="utf-8",
    )
    topic = Topic.from_markdown(path)
    assert topic.id == "demo-1"
    assert topic.field == "nlp"
    assert topic.budget.gpu_hours == 10
    assert "Budget constraints" in topic.to_markdown()
    assert "public data only" in topic.to_markdown()
    assert "A gap remains in X." in topic.body
