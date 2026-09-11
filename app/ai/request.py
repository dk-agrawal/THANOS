from dataclasses import dataclass
from enum import Enum


class RequestType(str, Enum):

    CHAT = "chat"
    TOOL = "tool"
    RESEARCH = "research"
    CALCULATION = "calculation"


@dataclass(frozen=True)
class AIRequest:

    user_input: str
    request_type: RequestType = RequestType.CHAT
    provider: str | None = None
    request_types: tuple[RequestType, ...] = ()

    def __post_init__(self):

        if not self.request_types:
            object.__setattr__(
                self,
                "request_types",
                (self.request_type,),
            )

    def has_type(
        self,
        request_type: RequestType,
    ) -> bool:

        return request_type in self.request_types

    def to_dict(self) -> dict:

        return {
            "user_input": self.user_input,
            "request_type": self.request_type.value,
            "request_types": [
                request_type.value
                for request_type
                in self.request_types
            ],
            "provider": self.provider,
        }