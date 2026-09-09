from dataclasses import dataclass


@dataclass
class MemoryConflict:
    key: str
    old_value: str
    new_value: str
    conflict: bool
    reason: str


class MemoryConflictDetector:

    def detect(
        self,
        key: str,
        old_value: str | None,
        new_value: str,
    ) -> MemoryConflict:

        if old_value is None:

            return MemoryConflict(
                key=key,
                old_value="",
                new_value=new_value,
                conflict=False,
                reason="No existing memory found.",
            )

        old_normalized = self._normalize(
            old_value
        )

        new_normalized = self._normalize(
            new_value
        )

        if old_normalized == new_normalized:

            return MemoryConflict(
                key=key,
                old_value=old_value,
                new_value=new_value,
                conflict=False,
                reason="Memory value is unchanged.",
            )

        return MemoryConflict(
            key=key,
            old_value=old_value,
            new_value=new_value,
            conflict=True,
            reason=(
                "Existing memory value differs "
                "from the new value."
            ),
        )

    @staticmethod
    def _normalize(
        value: str,
    ) -> str:

        return (
            value.strip()
            .lower()
        )