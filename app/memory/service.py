from app.memory.history import MemoryHistory
from app.memory.long_term import LongTermMemory
from app.memory.models import MemoryCategory
from app.memory.pending import PendingMemoryStore
from app.memory.result import MemoryOperationResult


class MemoryService:

    def __init__(
        self,
        memory: LongTermMemory | None = None,
        pending_store: PendingMemoryStore | None = None,
        history: MemoryHistory | None = None,
    ):
        self.history = (
            history or MemoryHistory()
        )

        self.memory = (
            memory
            or LongTermMemory(
                history=self.history
            )
        )

        self.pending_store = (
            pending_store
            or PendingMemoryStore()
        )

    def remember(
        self,
        key: str,
        value: str,
        category: MemoryCategory = MemoryCategory.GENERAL,
        confidence: float = 1.0,
    ) -> MemoryOperationResult:

        return self.memory.remember(
            key=key,
            value=value,
            category=category,
            confidence=confidence,
        )

    def recall(
        self,
        key: str,
    ) -> str | None:

        return self.memory.recall(key)

    def forget(
        self,
        key: str,
    ) -> MemoryOperationResult | None:

        return self.memory.forget(key)

    def list_memories(self) -> dict:

        return self.memory.load()

    def list_pending(self) -> list[dict]:

        return self.pending_store.load()

    def remove_pending(
        self,
        key: str,
    ) -> bool:

        memories = self.pending_store.load()

        exists = any(
            memory.get("key") == key
            for memory in memories
        )

        if not exists:
            return False

        self.pending_store.remove(key)

        return True

    def confirm_pending(
        self,
        key: str,
    ) -> MemoryOperationResult | None:

        memories = self.pending_store.load()

        pending_memory = None

        for memory in memories:

            if memory.get("key") == key:
                pending_memory = memory
                break

        if pending_memory is None:
            return None

        category_value = pending_memory.get(
            "category",
            MemoryCategory.GENERAL.value,
        )

        try:

            category = MemoryCategory(
                category_value
            )

        except ValueError:

            category = MemoryCategory.GENERAL

        result = self.remember(
            key=pending_memory["key"],
            value=pending_memory["value"],
            category=category,
            confidence=float(
                pending_memory.get(
                    "confidence",
                    1.0,
                )
            ),
        )

        self.remove_pending(key)

        return result

    def get_history(
        self,
        key: str,
    ) -> list[dict]:

        return self.history.get_for_key(
            key
        )