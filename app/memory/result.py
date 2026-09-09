from dataclasses import dataclass


@dataclass
class MemoryOperationResult:
    key: str
    value: str
    action: str
    old_value: str | None = None

    @property
    def created(self) -> bool:
        return self.action == "created"

    @property
    def updated(self) -> bool:
        return self.action == "updated"

    @property
    def unchanged(self) -> bool:
        return self.action == "unchanged"

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "value": self.value,
            "action": self.action,
            "old_value": self.old_value,
        }