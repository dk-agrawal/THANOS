from app.agents.goal_requirements import (
    GoalRequirement,
    GoalRequirements,
    RequirementStatus,
)


def test_requirement_starts_as_pending():

    requirement = GoalRequirement(
        name="weather",
        description="Get weather information.",
    )

    assert (
        requirement.status
        == RequirementStatus.PENDING
    )

    assert requirement.is_complete is False


def test_requirement_can_be_completed():

    requirement = GoalRequirement(
        name="weather",
        description="Get weather information.",
    )

    requirement.complete()

    assert (
        requirement.status
        == RequirementStatus.COMPLETE
    )

    assert requirement.is_complete is True


def test_requirement_can_be_failed():

    requirement = GoalRequirement(
        name="weather",
        description="Get weather information.",
    )

    requirement.fail()

    assert (
        requirement.status
        == RequirementStatus.FAILED
    )

    assert requirement.is_complete is False


def test_requirements_can_be_added():

    requirements = GoalRequirements(
        goal="Get weather and news.",
    )

    requirement = requirements.add(
        name="weather",
        description="Get weather information.",
    )

    assert requirement.name == "weather"
    assert requirement.description == (
        "Get weather information."
    )

    assert len(requirements.requirements) == 1


def test_requirement_can_be_retrieved():

    requirements = GoalRequirements(
        goal="Get weather and news.",
    )

    requirements.add(
        name="weather",
        description="Get weather information.",
    )

    requirement = requirements.get("weather")

    assert requirement is not None
    assert requirement.name == "weather"


def test_missing_requirement_returns_none():

    requirements = GoalRequirements(
        goal="Get weather.",
    )

    assert requirements.get("weather") is None


def test_requirement_can_be_completed_by_name():

    requirements = GoalRequirements(
        goal="Get weather.",
    )

    requirements.add(
        name="weather",
        description="Get weather information.",
    )

    assert requirements.complete("weather") is True

    assert (
        requirements.get("weather").status
        == RequirementStatus.COMPLETE
    )


def test_missing_requirement_cannot_be_completed():

    requirements = GoalRequirements(
        goal="Get weather.",
    )

    assert requirements.complete("weather") is False


def test_requirement_can_be_failed_by_name():

    requirements = GoalRequirements(
        goal="Get weather.",
    )

    requirements.add(
        name="weather",
        description="Get weather information.",
    )

    assert requirements.fail("weather") is True

    assert (
        requirements.get("weather").status
        == RequirementStatus.FAILED
    )


def test_missing_requirement_cannot_be_failed():

    requirements = GoalRequirements(
        goal="Get weather.",
    )

    assert requirements.fail("weather") is False


def test_pending_requirements_are_tracked():

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

    assert [
        requirement.name
        for requirement in requirements.pending
    ] == ["news"]


def test_completed_requirements_are_tracked():

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

    assert [
        requirement.name
        for requirement in requirements.completed
    ] == ["weather"]


def test_failed_requirements_are_tracked():

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

    requirements.fail("news")

    assert [
        requirement.name
        for requirement in requirements.failed
    ] == ["news"]


def test_all_requirements_complete_means_goal_complete():

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
    requirements.complete("news")

    assert requirements.is_complete is True


def test_pending_requirement_means_goal_not_complete():

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

    assert requirements.is_complete is False


def test_failed_requirement_means_goal_not_complete():

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
    requirements.fail("news")

    assert requirements.is_complete is False


def test_empty_requirements_are_not_complete():

    requirements = GoalRequirements(
        goal="Get weather.",
    )

    assert requirements.is_complete is False


def test_empty_requirement_name_is_rejected():

    requirements = GoalRequirements(
        goal="Get weather.",
    )

    try:
        requirements.add(
            name="",
            description="Get weather information.",
        )
    except ValueError as error:
        assert str(error) == (
            "Requirement name cannot be empty."
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_empty_requirement_description_is_rejected():

    requirements = GoalRequirements(
        goal="Get weather.",
    )

    try:
        requirements.add(
            name="weather",
            description="",
        )
    except ValueError as error:
        assert str(error) == (
            "Requirement description cannot be empty."
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_requirement_can_be_serialized():

    requirement = GoalRequirement(
        name="weather",
        description="Get weather information.",
    )

    payload = requirement.to_dict()

    assert payload == {
        "name": "weather",
        "description": "Get weather information.",
        "status": "pending",
        "is_complete": False,
    }


def test_goal_requirements_can_be_serialized():

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
    requirements.fail("news")

    payload = requirements.to_dict()

    assert payload == {
        "goal": "Get weather and news.",
        "requirements": [
            {
                "name": "weather",
                "description": "Get weather information.",
                "status": "complete",
                "is_complete": True,
            },
            {
                "name": "news",
                "description": "Get latest news.",
                "status": "failed",
                "is_complete": False,
            },
        ],
        "pending": [],
        "completed": ["weather"],
        "failed": ["news"],
        "is_complete": False,
    }
    