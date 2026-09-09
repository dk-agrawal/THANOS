from app.api.github import GitHubProvider
from app.tools.base import Tool
from app.tools.result import ToolResult


class GitHubTool(Tool):

    def __init__(self, api_registry):
        self.provider = api_registry.get("github")

    @property
    def name(self) -> str:
        return "github_search"

    @property
    def description(self) -> str:
        return (
            "Searches GitHub repositories and returns "
            "useful repository information."
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "Repository search query, for example "
                        "'python cybersecurity'."
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
            result = await self.provider.search_repositories(
                query=query,
                per_page=5,
            )

            repositories = []

            for item in result.get("items", []):

                repositories.append(
                    {
                        "name": item.get("full_name"),
                        "description": item.get(
                            "description"
                        ),
                        "url": item.get("html_url"),
                        "stars": item.get(
                            "stargazers_count"
                        ),
                        "language": item.get(
                            "language"
                        ),
                        "forks": item.get(
                            "forks_count"
                        ),
                        "updated_at": item.get(
                            "updated_at"
                        ),
                    }
                )

            return ToolResult(
                success=True,
                data={
                    "query": query,
                    "total_results": result.get(
                        "total_count",
                        0,
                    ),
                    "repositories": repositories,
                },
            )

        except Exception as error:

            return ToolResult(
                success=False,
                error=f"GitHub search failed: {error}",
            )