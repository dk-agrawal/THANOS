
from app.agents.goal_requirements import (
    GoalRequirements,
)
from app.agents.requirement_resolver import (
    RequirementResolver,
)


def test_resolves_next_pending_requirement():

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

    resolution = RequirementResolver().resolve(
        requirements
    )

    assert resolution.found is True
    assert resolution.requirement.name == "github"


def test_selects_first_pending_requirement():

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

    resolution = RequirementResolver().resolve(
        requirements
    )

    assert resolution.requirement.name == "weather"


def test_failed_requirement_selected_when_no_pending():

    requirements = GoalRequirements(
        goal="Get weather.",
    )

    requirements.add(
        name="weather",
        description="Get weather information.",
    )
    requirements.fail("weather")

    resolution = RequirementResolver().resolve(
        requirements
    )

    assert resolution.found is True
    assert resolution.requirement.name == "weather"
    assert "recovery" in resolution.reason


def test_no_requirement_returned_when_all_complete():

    requirements = GoalRequirements(
        goal="Get weather.",
    )

    requirements.add(
        name="weather",
        description="Get weather information.",
    )
    requirements.complete("weather")

    resolution = RequirementResolver().resolve(
        requirements
    )

    assert resolution.found is False
    assert resolution.requirement is None


def test_empty_requirements_return_no_target():

    requirements = GoalRequirements(
        goal="Get information.",
    )

    resolution = RequirementResolver().resolve(
        requirements
    )

    assert resolution.found is False


def test_pending_requirement_precedes_failed_requirement():

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

    resolution = RequirementResolver().resolve(
        requirements
    )

    assert resolution.requirement.name == "news"


def test_invalid_requirements_are_rejected():

    try:
        RequirementResolver().resolve(None)
    except ValueError as error:
        assert str(error) == "Invalid goal requirements."
    else:
        raise AssertionError("Expected ValueError")


def test_resolution_can_be_serialized():

    requirements = GoalRequirements(
        goal="Get weather.",
    )

    requirements.add(
        name="weather",
        description="Get weather information.",
    )

    resolution = RequirementResolver().resolve(
        requirements
    )

    assert resolution.to_dict() == {
        "found": True,
        "requirement": {
            "name": "weather",
            "description": "Get weather information.",
            "status": "pending",
            "is_complete": False,
        },
        "reason": "Selected the next pending goal requirement.",
    }
