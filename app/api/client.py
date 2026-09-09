import httpx


class APIClient:

    def __init__(self, timeout: float = 15.0):
        self.timeout = timeout

    async def get(
        self,
        url: str,
        *,
        params: dict | None = None,
        headers: dict | None = None,
    ) -> dict:

        async with httpx.AsyncClient(
            timeout=self.timeout
        ) as client:

            response = await client.get(
                url,
                params=params,
                headers=headers,
            )

            response.raise_for_status()

            return response.json()

    async def post(
        self,
        url: str,
        *,
        json: dict | None = None,
        headers: dict | None = None,
    ) -> dict:

        async with httpx.AsyncClient(
            timeout=self.timeout
        ) as client:

            response = await client.post(
                url,
                json=json,
                headers=headers,
            )

            response.raise_for_status()

            return response.json()