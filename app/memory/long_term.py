import json
from datetime import datetime, timezone
from pathlib import Path

from app.memory.conflict import MemoryConflictDetector
from app.memory.history import MemoryHistory
from app.memory.models import MemoryCategory, MemoryRecord
from app.memory.result import MemoryOperationResult


class LongTermMemory:

    def __init__(
        self,
        file_path: str = "data/long_term_memory.json",
        history: MemoryHistory | None = None,
        conflict_detector: MemoryConflictDetector | None = None,
    ):
        self.file_path = Path(file_path)

        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not self.file_path.exists():
            self._save({})

        self.history = (
            history or MemoryHistory()
        )

        self.conflict_detector = (
            conflict_detector
            or MemoryConflictDetector()
        )

    def remember(
        self,
        key: str,
        value: str,
        category: MemoryCategory = MemoryCategory.GENERAL,
        confidence: float = 1.0,
    ) -> MemoryOperationResult:

        memory = self.load()

        existing = memory.get(key)

        now = datetime.now(
            timezone.utc
        ).isoformat()

        if isinstance(existing, dict):

            created_at = existing.get(
                "created_at",
                now,
            )

            old_value = existing.get(
                "value"
            )

        elif isinstance(existing, str):

            created_at = now
            old_value = existing

        else:

            created_at = now
            old_value = None

        conflict = self.conflict_detector.detect(
            key=key,
            old_value=old_value,
            new_value=value,
        )

        if old_value is None:

            action = "created"

        elif not conflict.conflict:

            return MemoryOperationResult(
                key=key,
                value=value,
                action="unchanged",
                old_value=old_value,
            )

        else:

            action = "updated"

        record = MemoryRecord(
            key=key,
            value=value,
            category=category,
            confidence=confidence,
            created_at=created_at,
            updated_at=now,
        )

        memory[key] = record.to_dict()

        self._save(memory)

        self.history.add(
            key=key,
            old_value=old_value,
            new_value=value,
            confidence=confidence,
        )

        return MemoryOperationResult(
            key=key,
            value=value,
            action=action,
            old_value=old_value,
        )

    def recall(
        self,
        key: str,
    ) -> str | None:

        memory = self.load()

        record = memory.get(key)

        if record is None:
            return None

        if isinstance(record, str):
            return record

        return record.get("value")

    def recall_record(
        self,
        key: str,
    ) -> MemoryRecord | None:

        memory = self.load()

        record = memory.get(key)

        if record is None:
            return None

        if isinstance(record, str):
            return MemoryRecord(
                key=key,
                value=record,
                category=MemoryCategory.GENERAL,
            )

        return MemoryRecord.from_dict(
            record
        )

    def load(self) -> dict:

        try:

            with open(
                self.file_path,
                "r",
                encoding="utf-8",
            ) as file:

                data = json.load(file)

            if isinstance(data, dict):
                return data

            return {}

        except (
            json.JSONDecodeError,
            OSError,
        ):

            return {}

    def forget(
        self,
        key: str,
    ) -> MemoryOperationResult | None:

        memory = self.load()

        existing = memory.get(key)

        if existing is None:

            return None

        if isinstance(existing, dict):

            old_value = existing.get(
                "value"
            )

            confidence = float(
                existing.get(
                    "confidence",
                    1.0,
                )
            )

        else:

            old_value = str(existing)
            confidence = 1.0

        del memory[key]

        self._save(memory)

        self.history.add(
            key=key,
            old_value=old_value,
            new_value="",
            confidence=confidence,
        )

        return MemoryOperationResult(
            key=key,
            value="",
            action="deleted",
            old_value=old_value,
        )

    def clear(self) -> None:
        self._save({})

    def _save(
        self,
        data: dict,
    ) -> None:

        with open(
            self.file_path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                indent=2,
                ensure_ascii=False,
            )