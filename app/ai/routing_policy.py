from dataclasses import dataclass

from app.ai.request import RequestType


@dataclass(frozen=True)
class RoutingDecision:

    request_type: RequestType
    provider: str
    use_tools: bool
    use_research: bool

    def to_dict(self) -> dict:

        return {
            "request_type": self.request_type.value,
            "provider": self.provider,
            "use_tools": self.use_tools,
            "use_research": self.use_research,
        }


class AIRoutingPolicy:

    def __init__(
        self,
        default_provider: str = "openrouter",
    ):
        if not default_provider:
            raise ValueError(
                "Default provider cannot be empty."
            )

        self.default_provider = (
            default_provider
        )

    def decide(
        self,
        request_type: RequestType,
        provider: str | None = None,
        request_types: tuple[RequestType, ...]
        | None = None,
    ) -> RoutingDecision:

        selected_provider = (
            provider
            or self.default_provider
        )

        types = (
            request_types
            or (request_type,)
        )

        use_research = (
            RequestType.RESEARCH in types
        )

        use_tools = (
            use_research
            or RequestType.CALCULATION in types
            or RequestType.TOOL in types
        )

        return RoutingDecision(
            request_type=request_type,
            provider=selected_provider,
            use_tools=use_tools,
            use_research=use_research,
        )