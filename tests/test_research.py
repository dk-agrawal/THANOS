from app.agents.research import ResearchEngine


class FakeToolExecutor:

    async def execute(
        self,
        tool_name: str,
        arguments: dict,
    ):

        class FakeResult:

            def __init__(self):
                self.success = True
                self.data = {
                    "articles": [
                        {
                            "title": "Cybersecurity Tools",
                            "description": (
                                "A useful cybersecurity tool."
                            ),
                            "url": (
                                "https://example.com"
                            ),
                            "publishedAt": (
                                "2026-09-05T00:00:00Z"
                            ),
                        }
                    ]
                }

            def to_dict(self):
                return {
                    "success": self.success,
                    "data": self.data,
                }

        return FakeResult()


def test_research_engine_creation():

    executor = FakeToolExecutor()

    research = ResearchEngine(
        executor
    )

    assert research is not None


async def run_research():

    executor = FakeToolExecutor()

    research = ResearchEngine(
        executor
    )

    return await research.research(
        "cybersecurity tools"
    )


def test_research_engine_research():

    import asyncio

    result = asyncio.run(
        run_research()
    )

    assert result

    assert result["query"] == (
        "cybersecurity tools"
    )

    assert "cleaned_query" in result

    assert "freshness_required" in result

    assert "sources_requested" in result

    assert "sources" in result

    assert "quality" in result

    assert isinstance(
        result["sources"],
        dict,
    )