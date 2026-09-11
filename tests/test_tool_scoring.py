from app.agents.tool_scoring import (
    ToolRelevanceScorer,
)


TOOL_KEYWORDS = {
    "weather": {
        "weather",
        "forecast",
        "rain",
        "temperature",
    },
    "news": {
        "news",
        "headlines",
        "current events",
    },
    "github": {
        "github",
        "repository",
        "repo",
        "commit",
    },
}


def test_scores_matching_keywords():

    scorer = ToolRelevanceScorer()

    result = scorer.score(
        user_input="What's the weather forecast?",
        tool_name="weather",
        keywords=TOOL_KEYWORDS["weather"],
    )

    assert result.tool_name == "weather"
    assert result.score == 2
    assert result.matched_keywords == (
        "forecast",
        "weather",
    )


def test_non_matching_tool_has_zero_score():

    scorer = ToolRelevanceScorer()

    result = scorer.score(
        user_input="Show me the latest news",
        tool_name="github",
        keywords=TOOL_KEYWORDS["github"],
    )

    assert result.score == 0
    assert result.matched_keywords == ()


def test_rank_orders_by_score():

    scorer = ToolRelevanceScorer()

    results = scorer.rank(
        user_input=(
            "Check the weather forecast "
            "and temperature"
        ),
        tool_keywords=TOOL_KEYWORDS,
    )

    assert results[0].tool_name == "weather"
    assert results[0].score == 3


def test_relevant_filters_zero_scores():

    scorer = ToolRelevanceScorer()

    results = scorer.relevant(
        user_input="Show me the latest news",
        tool_keywords=TOOL_KEYWORDS,
    )

    assert len(results) == 1
    assert results[0].tool_name == "news"


def test_minimum_score():

    scorer = ToolRelevanceScorer()

    results = scorer.relevant(
        user_input="weather forecast",
        tool_keywords=TOOL_KEYWORDS,
        minimum_score=2,
    )

    assert len(results) == 1
    assert results[0].tool_name == "weather"


def test_empty_input():

    scorer = ToolRelevanceScorer()

    result = scorer.score(
        user_input="   ",
        tool_name="weather",
        keywords=TOOL_KEYWORDS["weather"],
    )

    assert result.score == 0
    assert result.matched_keywords == ()


def test_to_dict():

    scorer = ToolRelevanceScorer()

    result = scorer.score(
        user_input="weather forecast",
        tool_name="weather",
        keywords=TOOL_KEYWORDS["weather"],
    )

    assert result.to_dict() == {
        "tool_name": "weather",
        "score": 2,
        "matched_keywords": [
            "forecast",
            "weather",
        ],
    }