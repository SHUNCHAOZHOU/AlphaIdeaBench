from alphaideabench.core.tools import RunContext
from alphaideabench.domain.topic import Budget, Topic
from alphaideabench.tools.builtin import bound_registry

JUDGE_TOOLS = ["load_topic", "load_budget", "load_idea", "load_rubric"]


def _ctx() -> RunContext:
    topic = Topic(
        id="t1",
        title="Demo",
        budget=Budget(gpu="1x 4090", gpu_hours=40),
        body="gap",
    )
    return RunContext(topic=topic, dimension_id="data_feasibility")


def test_unknown_tool_does_not_raise():
    registry = bound_registry(JUDGE_TOOLS)
    out = registry.execute("definitely_not_a_tool", {}, _ctx())
    assert "Unknown tool" in out
    assert "load_topic" in out


def test_invoke_envelope_is_unwrapped():
    registry = bound_registry(JUDGE_TOOLS)
    out = registry.execute("invoke", {"name": "load_budget", "parameters": {}}, _ctx())
    assert "1x 4090" in out


def test_invoke_envelope_with_unknown_inner_tool_reports_error():
    registry = bound_registry(JUDGE_TOOLS)
    out = registry.execute("invoke", {"name": "search_papers"}, _ctx())
    assert "Unknown tool" in out


def test_known_tool_still_works():
    registry = bound_registry(JUDGE_TOOLS)
    assert "Data Feasibility" in registry.execute("load_rubric", {}, _ctx())
