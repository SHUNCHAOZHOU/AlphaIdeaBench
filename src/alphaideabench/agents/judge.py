from __future__ import annotations

from alphaideabench.config import Settings
from alphaideabench.core.agent import Agent, AgentResult
from alphaideabench.core.llm import LLMBackend
from alphaideabench.core.prompt import render_file
from alphaideabench.core.tools import RunContext
from alphaideabench.domain.dimensions import DimensionSpec, load_catalog
from alphaideabench.domain.idea import ResearchIdea
from alphaideabench.domain.score import DimensionJudgment
from alphaideabench.domain.topic import Topic
from alphaideabench.tools.builtin import bound_registry


class DimensionJudge:
    def __init__(self, settings: Settings, backend: LLMBackend) -> None:
        self.settings = settings
        self.backend = backend
        self.spec = settings.agents.judge
        self.catalog = load_catalog()

    def judge(
        self,
        topic: Topic,
        idea: ResearchIdea,
        dimension_id: str,
        repeat_index: int = 0,
    ) -> tuple[DimensionJudgment, AgentResult]:
        dimension: DimensionSpec = self.catalog.dimensions[dimension_id]
        ctx = RunContext(topic=topic, idea=idea, dimension_id=dimension_id)
        agent = Agent(
            name=f"{self.spec.name}:{dimension_id}",
            backend=self.backend,
            system_prompt=render_file(
                self.spec.system_prompt, topic=topic, idea=idea, dimension=dimension
            ),
            tools=bound_registry(self.spec.tools),
            ctx=ctx,
            temperature=self.spec.temperature,
            max_rounds=self.spec.max_rounds,
            require_json=True,
            json_mode=self.settings.llm.json_mode,
            model=self.spec.model,
        )
        user_message = render_file(
            self.spec.user_prompt, topic=topic, idea=idea, dimension=dimension
        )
        result = agent.run(user_message)
        if not result.parsed:
            raise RuntimeError(f"Judge `{dimension_id}` returned no JSON.")
        judgment = DimensionJudgment.from_llm(
            result.parsed,
            dimension_id,
            repeat_index,
            expected_checklist=dimension.checklist_texts,
        )
        return judgment, result
