class ResearchQualityGate:

    MIN_SOURCE_SCORE = 50
    MIN_RESULT_SCORE = 50

    def validate(
        self,
        research_data: dict,
    ) -> dict:

        sources = research_data.get(
            "sources",
            {},
        )

        if not sources:
            return {
                "passed": False,
                "reason": "No research sources available.",
            }

        successful_sources = 0
        useful_items = 0
        best_score = 0

        for source_data in sources.values():

            source_score = source_data.get(
                "score",
                {},
            ).get(
                "value",
                0,
            )

            if source_score >= self.MIN_SOURCE_SCORE:
                successful_sources += 1

            items = source_data.get(
                "items",
                [],
            )

            for item in items:

                result_score = item.get(
                    "score",
                    {},
                ).get(
                    "value",
                    0,
                )

                if result_score >= self.MIN_RESULT_SCORE:
                    useful_items += 1

                    best_score = max(
                        best_score,
                        result_score,
                    )

        if successful_sources == 0:
            return {
                "passed": False,
                "reason": (
                    "Available research sources "
                    "did not meet the quality threshold."
                ),
            }

        if useful_items == 0:
            return {
                "passed": False,
                "reason": (
                    "Research sources returned no "
                    "useful results."
                ),
            }

        return {
            "passed": True,
            "reason": (
                "Research quality is sufficient."
            ),
            "successful_sources": successful_sources,
            "useful_items": useful_items,
            "best_result_score": best_score,
        }