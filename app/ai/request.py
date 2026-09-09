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

    def to_dict(self) -> dict:

        return {
            "user_input": self.user_input,
            "request_type": self.request_type.value,
            "provider": self.provider,
        }