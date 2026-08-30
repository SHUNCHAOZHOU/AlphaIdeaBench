"""AlphaIdeaBench: multi-agent idea generation and multi-dimensional evaluation."""

from alphaideabench.core.agent import Agent, AgentResult
from alphaideabench.core.llm import LLMBackend, MockBackend, OpenAIBackend
from alphaideabench.core.tools import RunContext, ToolRegistry, tool
from alphaideabench.domain.idea import ResearchIdea
from alphaideabench.domain.score import DimensionJudgment, Track1Result
from alphaideabench.domain.topic import Topic

__version__ = "0.1.0"
__all__ = [
    "Agent",
    "AgentResult",
    "DimensionJudgment",
    "LLMBackend",
    "MockBackend",
    "OpenAIBackend",
    "ResearchIdea",
    "RunContext",
    "ToolRegistry",
    "Topic",
    "Track1Result",
    "tool",
]
