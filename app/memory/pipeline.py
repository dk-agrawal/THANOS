from app.memory.confidence import MemoryConfidence
from app.memory.extractor import MemoryExtractor
from app.memory.factory import MemoryFactory
from app.memory.long_term import LongTermMemory
from app.memory.pending import PendingMemoryStore
from app.memory.validator import MemoryValidator


class MemoryPipeline:

    MIN_CONFIDENCE = 0.8

    def __init__(
        self,
        memory: LongTermMemory | None = None,
        extractor: MemoryExtractor | None = None,
        validator: MemoryValidator | None = None,
        factory: MemoryFactory | None = None,
        confidence: MemoryConfidence | None = None,
        pending_store: PendingMemoryStore | None = None,
    ):
        self.memory = memory or LongTermMemory()

        self.extractor = (
            extractor or MemoryExtractor()
        )

        self.validator = (
            validator or MemoryValidator()
        )

        self.factory = (
            factory or MemoryFactory()
        )

        self.confidence = (
            confidence or MemoryConfidence()
        )

        self.pending_store = (
            pending_store or PendingMemoryStore()
        )

    def process(
        self,
        text: str,
    ) -> list[dict]:

        candidates = self.extractor.extract(text)

        valid_candidates = (
            self.validator.validate_all(
                candidates
            )
        )

        saved = []

        for candidate in valid_candidates:

            confidence = self.confidence.calculate(
                candidate
            )

            record = self.factory.create(
                key=candidate.key,
                value=candidate.value,
                category=candidate.category,
                confidence=confidence,
            )

            # Strong memory → save permanently
            if self.confidence.is_strong(
                confidence,
                threshold=self.MIN_CONFIDENCE,
            ):

                self.memory.remember(
                    key=record.key,
                    value=record.value,
                    category=record.category,
                    confidence=record.confidence,
                )

                saved.append(
                    record.to_dict()
                )

            # Weak memory → save as pending
            else:

                self.pending_store.add(
                    record.to_dict()
                )

        return saved