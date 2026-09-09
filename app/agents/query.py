from dataclasses import dataclass


@dataclass
class ResearchQuery:

    original: str
    cleaned: str
    freshness: bool
    sources: list[str]


class ResearchQueryAnalyzer:

    FRESHNESS_KEYWORDS = {
        "latest",
        "recent",
        "today",
        "current",
        "new",
        "news",
        "this week",
        "this month",
    }

    def analyze(self, query: str) -> ResearchQuery:

        cleaned = query.strip()

        lowered = cleaned.lower()

        freshness = any(
            keyword in lowered
            for keyword in self.FRESHNESS_KEYWORDS
        )

        sources = [
            "news",
            "github",
        ]

        if "github" in lowered:
            sources = ["github", "news"]

        elif "news" in lowered:
            sources = ["news", "github"]

        return ResearchQuery(
            original=query,
            cleaned=cleaned,
            freshness=freshness,
            sources=sources,
        )