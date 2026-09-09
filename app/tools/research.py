from app.agents.research import ResearchEngine
from app.agents.synthesis import ResearchSynthesizer
# from app.ai.providers.openrouter import OpenRouterProvider
from app.tools.base import Tool
from app.tools.result import ToolResult
from app.tools.executor import ToolExecutor
from app.tools.registry import ToolRegistry


class ResearchTool(Tool):

    def __init__(self, registry: ToolRegistry, ai_registry):
        self.ai = ai_registry.get("openrouter")
        self.executor = ToolExecutor(registry)

        self.research_engine = ResearchEngine(
            self.executor
        )

        self.synthesizer = ResearchSynthesizer(
            self.ai
        )

    @property
    def name(self) -> str:
        return "research"

    @property
    def description(self) -> str:
        return (
            "Performs multi-source research using available "
            "information sources and produces a synthesized answer."
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "Research question or topic."
                    ),
                }
            },
            "required": ["query"],
        }

    async def execute(
        self,
        query: str,
    ) -> ToolResult:

        try:

            result = await (
                self.research_engine
                .research_and_synthesize(
                    query,
                    self.synthesizer,
                )
            )

            return ToolResult(
                success=True,
                data={
                    "query": query,
                    "answer": result,
                },
            )

        except Exception as error:

            return ToolResult(
                success=False,
                error=f"Research failed: {error}",
            )