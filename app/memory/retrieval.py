from app.memory.aliases import MemoryAliasRegistry
from app.memory.long_term import LongTermMemory


class MemoryRetriever:

    def __init__(
        self,
        memory: LongTermMemory | None = None,
        aliases: MemoryAliasRegistry | None = None,
    ):
        self.memory = memory or LongTermMemory()

        self.aliases = (
            aliases or MemoryAliasRegistry()
        )

    def get_all(self) -> dict:
        return self.memory.load()

    def search(
        self,
        query: str,
        limit: int = 5,
    ) -> dict:

        memories = self.get_all()

        if not memories:
            return {}

        query_words = self._tokenize(query)

        scored = []

        for key, record in memories.items():

            if isinstance(record, dict):

                memory_value = str(
                    record.get("value", "")
                )

            else:

                memory_value = str(record)

            key_words = self._tokenize(key)

            value_words = self._tokenize(
                memory_value
            )

            key_overlap = (
                query_words & key_words
            )

            value_overlap = (
                query_words & value_words
            )

            alias_score = 0

            for alias in self.aliases.get_aliases(
                key
            ):

                alias_words = self._tokenize(
                    alias
                )

                if alias_words.issubset(
                    query_words
                ):
                    alias_score += 3

            key_score = len(key_overlap) * 2
            value_score = len(value_overlap)

            score = (
                key_score
                + value_score
                + alias_score
            )

            if score > 0:

                scored.append(
                    (
                        score,
                        key,
                        memory_value,
                    )
                )

        scored.sort(
            key=lambda item: (
                item[0],
                item[1],
            ),
            reverse=True,
        )

        results = {}

        for _, key, value in scored[:limit]:

            results[key] = value

        return results

    def get_context(
        self,
        query: str | None = None,
        limit: int = 5,
    ) -> str:

        if query:

            memories = self.search(
                query=query,
                limit=limit,
            )

        else:

            memories = self.get_all()

        if not memories:
            return ""

        lines = [
            "Relevant long-term memories:"
        ]

        for key, value in memories.items():

            if isinstance(value, dict):

                value = value.get(
                    "value",
                    "",
                )

            lines.append(
                f"- {key}: {value}"
            )

        return "\n".join(lines)

    def has_memory(
        self,
        key: str,
    ) -> bool:

        return (
            self.memory.recall(key)
            is not None
        )

    @staticmethod
    def _tokenize(
        text: str,
    ) -> set[str]:

        cleaned = (
            text.lower()
            .replace("_", " ")
            .replace("-", " ")
            .replace(",", " ")
            .replace(".", " ")
            .replace("!", " ")
            .replace("?", " ")
            .replace(":", " ")
            .replace(";", " ")
        )

        words = cleaned.split()

        return {
            word
            for word in words
            if len(word) > 2
        }