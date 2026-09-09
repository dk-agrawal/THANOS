from app.memory.models import (
    MemoryCategory,
    MemoryRecord,
)


class MemoryFactory:

    def create(
        self,
        key: str,
        value: str,
        category: MemoryCategory = MemoryCategory.GENERAL,
        confidence: float = 1.0,
    ) -> MemoryRecord:

        confidence = max(
            0.0,
            min(
                1.0,
                confidence,
            ),
        )

        return MemoryRecord(
            key=key,
            value=value,
            category=category,
            confidence=confidence,
        )

    def from_dict(
        self,
        data: dict,
    ) -> MemoryRecord:

        return MemoryRecord.from_dict(
            data
        )