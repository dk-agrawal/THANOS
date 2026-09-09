import json

from app.ai.providers.openrouter import OpenRouterProvider


class ResearchSynthesizer:

    def __init__(
        self,
        ai: OpenRouterProvider,
    ):
        self.ai = ai

    async def synthesize(
        self,
        query: str,
        research_data: dict,
    ) -> str:

        prompt = f"""
You are THANOS research synthesizer.

User research query:
{query}

Research data:
{json.dumps(research_data, indent=2, default=str)}

Instructions:

- Use only the supplied research data.
- Do not invent facts.
- Treat source scores as reliability hints, not absolute truth.
- Prefer higher-scored successful sources when sources disagree.
- Do not use failed sources as factual evidence.
- Clearly distinguish information from different sources when useful.
- If only partial source data is available, answer using the available data.
- If the available data is insufficient, clearly say so.
- For freshness-sensitive queries, pay attention to the freshness_required field.
- Prefer concrete information over generic statements.
- Give a concise but useful answer.
"""

        response = await self.ai.generate(
            prompt
        )

        return response