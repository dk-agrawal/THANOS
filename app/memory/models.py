from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class MemoryCategory(str, Enum):
    IDENTITY = "identity"
    PREFERENCE = "preference"
    FAVORITE = "favorite"
    WORK = "work"
    SKILL = "skill"
    GENERAL = "general"


@dataclass
class MemoryRecord:
    key: str
    value: str
    category: MemoryCategory
    confidence: float = 1.0
    created_at: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "value": self.value,
            "category": self.category.value,
            "confidence": self.confidence,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "MemoryRecord":

        category = data.get(
            "category",
            MemoryCategory.GENERAL.value,
        )

        try:
            category = MemoryCategory(category)

        except ValueError:
            category = MemoryCategory.GENERAL

        now = datetime.now(
            timezone.utc
        ).isoformat()

        return cls(
            key=data.get("key", ""),
            value=data.get("value", ""),
            category=category,
            confidence=float(
                data.get(
                    "confidence",
                    1.0,
                )
            ),
            created_at=data.get(
                "created_at",
                now,
            ),
            updated_at=data.get(
                "updated_at",
                now,
            ),
        )