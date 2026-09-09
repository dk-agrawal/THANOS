from dataclasses import dataclass


@dataclass
class Message:

    role: str
    content: str


class ConversationContext:

    def __init__(
        self,
        max_messages: int = 20,
    ):
        self.max_messages = max_messages
        self._messages: list[Message] = []

    def add(
        self,
        role: str,
        content: str,
    ) -> None:

        self._messages.append(
            Message(
                role=role,
                content=content,
            )
        )

        self._trim()

    def get_messages(self) -> list[dict]:

        return [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in self._messages
        ]

    def clear(self) -> None:
        self._messages.clear()

    def size(self) -> int:
        return len(self._messages)

    def _trim(self) -> None:

        if len(self._messages) > self.max_messages:

            self._messages = self._messages[
                -self.max_messages:
            ]