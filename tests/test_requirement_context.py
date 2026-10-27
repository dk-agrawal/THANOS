
from app.agents.goal_requirements import (
    GoalRequirements,
)
from app.agents.requirement_context import (
    RequirementContextBuilder,
)


def test_builds_context_for_next_pending_requirement():

    requirements = GoalRequirements(
        goal="Get weather, news and GitHub information.",
    )

    requirements.add(
        name="weather",
        description="Get weather information.",
    )
    requirements.add(
        name="news",
        description="Get latest news.",
    )
    requirements.add(
        name="github",
        description="Get repository information.",
    )

    requirements.complete("weather")
    requirements.complete("news")

    context = RequirementContextBuilder().build(
        requirements
    )

    assert context is not None
    assert context.goal == (
        "Get weather, news and GitHub information."
    )
    assert context.target_name == "github"
    assert context.target_description == (
        "Get repository information."
    )
    assert context.pending_requirements == ("github",)
    assert context.completed_requirements == (
        "weather",
        "news",
    )
    assert context.failed_requirements == ()


def test_returns_none_when_all_requirements_complete():

    requirements = GoalRequirements(
        goal="Get weather.",
    )

    requirements.add(
        name="weather",
        description="Get weather information.",
    )
    requirements.complete("weather")

    context = RequirementContextBuilder().build(
        requirements
    )

    assert context is None


def test_returns_none_when_no_requirements_exist():

    requirements = GoalRequirements(
        goal="Get information.",
    )

    context = RequirementContextBuilder().build(
        requirements
    )

    assert context is None


def test_includes_failed_requirements():

    requirements = GoalRequirements(
        goal="Get weather and news.",
    )

    requirements.add(
        name="weather",
        description="Get weather information.",
    )
    requirements.add(
        name="news",
        description="Get latest news.",
    )

    requirements.fail("weather")

    context = RequirementContextBuilder().build(
        requirements
    )

    assert context is not None
    assert context.target_name == "news"
    assert context.pending_requirements == ("news",)
    assert context.failed_requirements == ("weather",)


def test_context_can_be_serialized():

    requirements = GoalRequirements(
        goal="Get weather and news.",
    )

    requirements.add(
        name="weather",
        description="Get weather information.",
    )
    requirements.add(
        name="news",
        description="Get latest news.",
    )

    requirements.complete("weather")

    context = RequirementContextBuilder().build(
        requirements
    )

    assert context is not None

    assert context.to_dict() == {
        "goal": "Get weather and news.",
        "target": {
            "name": "news",
            "description": "Get latest news.",
        },
        "pending_requirements": ["news"],
        "completed_requirements": ["weather"],
        "failed_requirements": [],
    }


def test_invalid_requirements_are_rejected():

    try:
        RequirementContextBuilder().build(None)
    except ValueError as error:
        assert str(error) == "Invalid goal requirements."
    else:
        raise AssertionError("Expected ValueError")
