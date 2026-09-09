from app.memory.context import ConversationContext
from app.memory.storage import MemoryStorage


class MemoryManager:

    def __init__(
        self,
        max_messages: int = 20,
        storage: MemoryStorage | None = None,
    ):
        self.context = ConversationContext(
            max_messages=max_messages
        )

        self.storage = storage or MemoryStorage()

        self._load_memory()

    def add_user_message(
        self,
        content: str,
    ) -> None:

        self.context.add(
            role="user",
            content=content,
        )

        self._save_memory()

    def add_assistant_message(
        self,
        content: str,
    ) -> None:

        self.context.add(
            role="assistant",
            content=content,
        )

        self._save_memory()

    def get_context(self) -> list[dict]:

        return self.context.get_messages()

    def clear(self) -> None:

        self.context.clear()
        self.storage.clear()

    def size(self) -> int:

        return self.context.size()

    def _load_memory(self) -> None:

        messages = self.storage.load()

        for message in messages:

            role = message.get("role")
            content = message.get("content")

            if not role or content is None:
                continue

            self.context.add(
                role=role,
                content=content,
            )

    def _save_memory(self) -> None:

        self.storage.save(
            self.context.get_messages()
        )