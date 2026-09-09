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
    ) -> RoutingDecision:

        selected_provider = (
            provider
            or self.default_provider
        )

        if request_type == RequestType.CHAT:

            return RoutingDecision(
                request_type=request_type,
                provider=selected_provider,
                use_tools=False,
                use_research=False,
            )

        if request_type == RequestType.CALCULATION:

            return RoutingDecision(
                request_type=request_type,
                provider=selected_provider,
                use_tools=True,
                use_research=False,
            )

        if request_type == RequestType.TOOL:

            return RoutingDecision(
                request_type=request_type,
                provider=selected_provider,
                use_tools=True,
                use_research=False,
            )

        if request_type == RequestType.RESEARCH:

            return RoutingDecision(
                request_type=request_type,
                provider=selected_provider,
                use_tools=True,
                use_research=True,
            )

        raise ValueError(
            f"Unsupported request type: "
            f"{request_type}"
        )