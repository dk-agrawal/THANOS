import asyncio

from app.agents.synthesis import ResearchSynthesizer


class FakeAIProvider:

    async def generate(
        self,
        prompt: str,
    ) -> str:

        return (
            "Cybersecurity tools help "
            "protect systems and data."
        )


def test_research_synthesizer_creation():

    ai = FakeAIProvider()

    synthesizer = ResearchSynthesizer(
        ai
    )

    assert synthesizer is not None


def test_research_synthesizer():

    ai = FakeAIProvider()

    synthesizer = ResearchSynthesizer(
        ai
    )

    research_data = {
        "query": "cybersecurity tools",
        "cleaned_query": "cybersecurity tools",
        "freshness_required": False,
        "sources_requested": [
            "news",
            "github",
        ],
        "sources": {},
        "quality": {
            "passed": True,
            "reason": (
                "Research quality is sufficient."
            ),
        },
    }

    result = asyncio.run(
        synthesizer.synthesize(
            query="cybersecurity tools",
            research_data=research_data,
        )
    )

    assert result

    assert isinstance(
        result,
        str,
    )

    assert (
        "Cybersecurity tools"
        in result
    )