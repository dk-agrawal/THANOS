import httpx

from app.ai.provider import AIProvider
from app.core.config import settings


class OpenRouterProvider(AIProvider):

    async def generate(self, prompt: str) -> str:
        if not settings.OPENROUTER_API_KEY:
            raise RuntimeError("OPENROUTER_API_KEY is not configured")

        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": settings.AI_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.OPENROUTER_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
            )

        response.raise_for_status()

        data = response.json()

        return data["choices"][0]["message"]["content"]

    async def generate_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
    ) -> dict:

        if not settings.OPENROUTER_API_KEY:
            raise RuntimeError("OPENROUTER_API_KEY is not configured")

        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": settings.AI_MODEL,
            "messages": messages,
            "tools": tools,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.OPENROUTER_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
            )

        response.raise_for_status()

        return response.json()