from app.memory.extractor import MemoryCandidate


class MemoryValidator:

    MAX_KEY_LENGTH = 100
    MAX_VALUE_LENGTH = 500

    def validate(
        self,
        candidate: MemoryCandidate,
    ) -> bool:

        if not candidate.key:
            return False

        if not candidate.value:
            return False

        if len(candidate.key) > self.MAX_KEY_LENGTH:
            return False

        if len(candidate.value) > self.MAX_VALUE_LENGTH:
            return False

        return True

    def validate_all(
        self,
        candidates: list[MemoryCandidate],
    ) -> list[MemoryCandidate]:

        valid = []

        for candidate in candidates:

            if self.validate(candidate):
                valid.append(candidate)

        return valid