from app.memory.extractor import MemoryCandidate


class MemoryConfidence:

    def calculate(
        self,
        candidate: MemoryCandidate,
    ) -> float:

        text = candidate.value.lower()

        uncertain_words = {
            "maybe",
            "might",
            "perhaps",
            "probably",
            "think",
            "guess",
            "possibly",
        }

        words = set(
            text.replace(
                ",",
                " ",
            ).split()
        )

        if words.intersection(
            uncertain_words
        ):
            return 0.6

        return 1.0

    def is_strong(
        self,
        confidence: float,
        threshold: float = 0.8,
    ) -> bool:

        return confidence >= threshold