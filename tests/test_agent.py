from alphaideabench.core.agent import Agent
from alphaideabench.core.llm import MockBackend
from alphaideabench.core.tools import RunContext
from alphaideabench.core.types import ChatResult, ToolCallRequest
from alphaideabench.domain.topic import Budget, Topic
from alphaideabench.tools.builtin import bound_registry


def test_agent_tool_loop_then_json():
    topic = Topic(
        id="t1",
        title="Demo",
        field="nlp",
        budget=Budget(gpu="1x 4090", gpu_hours=8, notes="no api"),
        body="Existing work leaves gap Y.",
    )
    backend = MockBackend(
        script=[
            ChatResult(
                content=None,
                tool_calls=[ToolCallRequest(id="call_1", name="load_topic", arguments={})],
            ),
            ChatResult(content='{"title": "From tool context", "research_question": "Does Y hold?", "hypothesis": "h"}'),
        ]
    )
    agent = Agent(
        name="tester",
        backend=backend,
        system_prompt="You are a test agent.",
        tools=bound_registry(["load_topic"]),
        ctx=RunContext(topic=topic),
        require_json=True,
        max_rounds=4,
    )
    result = agent.run("generate")
    assert result.parsed is not None
    assert result.parsed["title"] == "From tool context"
    assert result.tool_trace[0]["name"] == "load_topic"
    assert "gap Y" in result.tool_trace[0]["output"]
    assert result.rounds == 2
