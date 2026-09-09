import json
from datetime import datetime, timezone
from pathlib import Path


class MemoryHistory:

    def __init__(
        self,
        file_path: str = "data/memory_history.json",
    ):
        self.file_path = Path(file_path)

        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not self.file_path.exists():
            self._save([])

    def add(
        self,
        key: str,
        old_value: str | None,
        new_value: str,
        confidence: float,
    ) -> None:

        history = self.load()

        history.append(
            {
                "key": key,
                "old_value": old_value,
                "new_value": new_value,
                "confidence": confidence,
                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat(),
            }
        )

        self._save(history)

    def load(self) -> list[dict]:

        try:

            with open(
                self.file_path,
                "r",
                encoding="utf-8",
            ) as file:

                data = json.load(file)

            if isinstance(data, list):
                return data

            return []

        except (
            json.JSONDecodeError,
            OSError,
        ):

            return []

    def get_for_key(
        self,
        key: str,
    ) -> list[dict]:

        return [
            entry
            for entry in self.load()
            if entry.get("key") == key
        ]

    def clear(self) -> None:
        self._save([])

    def _save(
        self,
        data: list[dict],
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