from dataclasses import dataclass

from app.memory.models import MemoryCategory


@dataclass
class MemoryCandidate:

    key: str
    value: str
    category: MemoryCategory
    reason: str


class MemoryExtractor:

    MEMORY_PATTERNS = {
        "my name is ": (
            "name",
            MemoryCategory.IDENTITY,
        ),
        "i am ": (
            "identity",
            MemoryCategory.IDENTITY,
        ),
        "i prefer ": (
            "preference",
            MemoryCategory.PREFERENCE,
        ),
        "i like ": (
            "preference",
            MemoryCategory.PREFERENCE,
        ),
        "i love ": (
            "preference",
            MemoryCategory.PREFERENCE,
        ),
        "my favorite ": (
            "favorite",
            MemoryCategory.FAVORITE,
        ),
        "i use ": (
            "usage",
            MemoryCategory.GENERAL,
        ),
        "i work with ": (
            "work",
            MemoryCategory.WORK,
        ),
    }

    def extract(
        self,
        text: str,
    ) -> list[MemoryCandidate]:

        cleaned = text.strip()

        if not cleaned:
            return []

        lowered = cleaned.lower()

        candidates = []

        for pattern, (
            key_type,
            category,
        ) in self.MEMORY_PATTERNS.items():

            if pattern not in lowered:
                continue

            start = lowered.find(pattern)

            value_start = (
                start + len(pattern)
            )

            value = cleaned[value_start:].strip()

            if not value:
                continue

            value = value.rstrip(".!?")

            key, value = self._normalize(
                key_type=key_type,
                value=value,
            )

            if not key or not value:
                continue

            candidates.append(
                MemoryCandidate(
                    key=key,
                    value=value,
                    category=category,
                    reason=(
                        f"Detected memory pattern: "
                        f"'{pattern.strip()}'."
                    ),
                )
            )

        return candidates

    @staticmethod
    def _normalize(
        key_type: str,
        value: str,
    ) -> tuple[str, str]:

        value = value.strip()

        if key_type == "name":

            value = MemoryExtractor._remove_prefix(
                value,
                "is ",
            )

            return (
                "name",
                value,
            )

        if key_type == "favorite":

            parts = value.split(
                " is ",
                1,
            )

            if len(parts) == 2:

                subject = parts[0].strip()
                actual_value = parts[1].strip()

                key = (
                    "favorite_"
                    + subject.lower()
                    .replace(" ", "_")
                )

                return (
                    key,
                    actual_value,
                )

            return (
                "favorite",
                value,
            )

        if key_type == "preference":

            return (
                "preference",
                value,
            )

        if key_type == "identity":

            return (
                "identity",
                value,
            )

        if key_type == "usage":

            return (
                "usage",
                value,
            )

        if key_type == "work":

            return (
                "work",
                value,
            )

        return (
            key_type,
            value,
        )

    @staticmethod
    def _remove_prefix(
        value: str,
        prefix: str,
    ) -> str:

        if value.lower().startswith(
            prefix.lower()
        ):

            return value[
                len(prefix):
            ].strip()

        return value