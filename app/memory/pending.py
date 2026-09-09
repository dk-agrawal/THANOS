import json
from pathlib import Path


class PendingMemoryStore:

    def __init__(
        self,
        file_path: str = "data/pending_memories.json",
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
        memory: dict,
    ) -> None:

        memories = self.load()

        memories.append(
            memory
        )

        self._save(memories)

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

    def remove(
        self,
        key: str,
    ) -> None:

        memories = self.load()

        memories = [
            memory
            for memory in memories
            if memory.get("key") != key
        ]

        self._save(memories)

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