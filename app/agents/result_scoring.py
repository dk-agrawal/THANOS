from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class ResultScore:

    score: int
    reason: str


class ResearchResultScorer:

    def score_news_article(
        self,
        article: dict,
        freshness_required: bool = False,
    ) -> ResultScore:

        score = 0
        reasons = []

        if article.get("title"):
            score += 20
            reasons.append(
                "Has a title."
            )

        if article.get("description"):
            score += 20
            reasons.append(
                "Has a description."
            )

        if article.get("url"):
            score += 20
            reasons.append(
                "Has source URL."
            )

        published_at = article.get(
            "published_at"
        )

        if published_at:
            score += 20
            reasons.append(
                "Has publication date."
            )

            if freshness_required:

                freshness_score = (
                    self._freshness_score(
                        published_at
                    )
                )

                score += freshness_score

                reasons.append(
                    f"Freshness score: "
                    f"{freshness_score}."
                )

        return ResultScore(
            score=min(score, 100),
            reason=" ".join(reasons),
        )

    def score_github_repository(
        self,
        repository: dict,
    ) -> ResultScore:

        score = 0
        reasons = []

        if repository.get("name"):
            score += 20
            reasons.append(
                "Has repository name."
            )

        if repository.get("description"):
            score += 20
            reasons.append(
                "Has description."
            )

        if repository.get("stars") is not None:
            score += 20
            reasons.append(
                "Has star information."
            )

        if repository.get("language"):
            score += 20
            reasons.append(
                "Has language information."
            )

        if repository.get("url"):
            score += 20
            reasons.append(
                "Has repository URL."
            )

        return ResultScore(
            score=score,
            reason=" ".join(reasons),
        )

    def _freshness_score(
        self,
        published_at: str,
    ) -> int:

        try:

            published = datetime.fromisoformat(
                published_at.replace(
                    "Z",
                    "+00:00",
                )
            )

            now = datetime.now(
                timezone.utc
            )

            age = now - published

            hours = age.total_seconds() / 3600

            if hours <= 24:
                return 20

            if hours <= 72:
                return 15

            if hours <= 168:
                return 10

            if hours <= 720:
                return 5

            return 0

        except (
            ValueError,
            TypeError,
        ):

            return 0