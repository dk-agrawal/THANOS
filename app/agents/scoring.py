from dataclasses import dataclass


@dataclass
class SourceScore:

    source: str
    score: int
    reason: str


class SourceScorer:

    SOURCE_SCORES = {
        "news": 70,
        "github": 80,
    }

    def score(
        self,
        source: str,
        result: dict,
    ) -> SourceScore:

        if not result.get("success", True):
            return SourceScore(
                source=source,
                score=0,
                reason="Source request failed.",
            )

        base_score = self.SOURCE_SCORES.get(
            source,
            50,
        )

        return SourceScore(
            source=source,
            score=base_score,
            reason="Source returned successfully.",
        )