import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ToolScore:

    tool_name: str
    score: int
    matched_keywords: tuple[str, ...]

    def to_dict(self) -> dict:

        return {
            "tool_name": self.tool_name,
            "score": self.score,
            "matched_keywords": list(
                self.matched_keywords
            ),
        }


class ToolRelevanceScorer:

    def score(
        self,
        user_input: str,
        tool_name: str,
        keywords: set[str],
    ) -> ToolScore:

        text = user_input.strip().lower()

        if not text:
            return ToolScore(
                tool_name=tool_name,
                score=0,
                matched_keywords=(),
            )

        matched = sorted(
            keyword
            for keyword in keywords
            if self._keyword_matches(
                text,
                keyword,
            )
        )

        score = len(matched)

        return ToolScore(
            tool_name=tool_name,
            score=score,
            matched_keywords=tuple(matched),
        )

    def rank(
        self,
        user_input: str,
        tool_keywords: dict[str, set[str]],
    ) -> list[ToolScore]:

        scores = [
            self.score(
                user_input=user_input,
                tool_name=tool_name,
                keywords=keywords,
            )
            for tool_name, keywords
            in tool_keywords.items()
        ]

        return sorted(
            scores,
            key=lambda item: (
                -item.score,
                item.tool_name,
            ),
        )

    def relevant(
        self,
        user_input: str,
        tool_keywords: dict[str, set[str]],
        minimum_score: int = 1,
    ) -> list[ToolScore]:

        ranked = self.rank(
            user_input=user_input,
            tool_keywords=tool_keywords,
        )

        return [
            result
            for result in ranked
            if result.score >= minimum_score
        ]

    @staticmethod
    def _keyword_matches(
        text: str,
        keyword: str,
    ) -> bool:

        pattern = (
            r"(?<!\w)"
            + re.escape(keyword.lower())
            + r"(?!\w)"
        )

        return re.search(
            pattern,
            text,
        ) is not None