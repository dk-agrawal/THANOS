import json
from pathlib import Path


class MemoryStorage:

    def __init__(
        self,
        file_path: str = "data/memory.json",
    ):
        self.file_path = Path(file_path)

        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not self.file_path.exists():
            self._save([])

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

    def save(
        self,
        messages: list[dict],
    ) -> None:

        with open(
            self.file_path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                messages,
                file,
                indent=2,
                ensure_ascii=False,
            )

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