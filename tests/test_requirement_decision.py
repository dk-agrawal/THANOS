from app.agents.goal_requirements import (
    GoalRequirements,
)
from app.agents.requirement_decision import (
    RequirementDecisionAction,
    RequirementDecisionEngine,
)


def test_all_requirements_complete():

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

    engine = RequirementDecisionEngine()

    decision = engine.decide(requirements)

    assert (
        decision.action
        == RequirementDecisionAction.COMPLETE
    )

    assert (
        "All goal requirements"
        in decision.reason
    )


def test_pending_requirements_mean_continue():

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

    engine = RequirementDecisionEngine()

    decision = engine.decide(requirements)

    assert (
        decision.action
        == RequirementDecisionAction.CONTINUE
    )

    assert "pending" in decision.reason


def test_failed_requirement_means_replan():

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

    engine = RequirementDecisionEngine()

    decision = engine.decide(requirements)

    assert (
        decision.action
        == RequirementDecisionAction.REPLAN
    )

    assert "failed" in decision.reason


def test_all_failed_requirements_mean_replan():

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
    requirements.fail("news")

    engine = RequirementDecisionEngine()

    decision = engine.decide(requirements)

    assert (
        decision.action
        == RequirementDecisionAction.REPLAN
    )


def test_no_requirements_means_continue():

    requirements = GoalRequirements(
        goal="Get information.",
    )

    engine = RequirementDecisionEngine()

    decision = engine.decide(requirements)

    assert (
        decision.action
        == RequirementDecisionAction.CONTINUE
    )


def test_invalid_requirements_are_rejected():

    engine = RequirementDecisionEngine()

    try:
        engine.decide(None)
    except ValueError as error:
        assert str(error) == (
            "Invalid goal requirements."
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_complete_decision_can_be_serialized():

    requirements = GoalRequirements(
        goal="Get weather.",
    )

    requirements.add(
        name="weather",
        description="Get weather information.",
    )

    requirements.complete("weather")

    engine = RequirementDecisionEngine()

    decision = engine.decide(requirements)

    payload = decision.to_dict()

    assert payload == {
        "action": "complete",
        "reason": (
            "All goal requirements have "
            "been completed."
        ),
    }


def test_continue_decision_can_be_serialized():

    requirements = GoalRequirements(
        goal="Get weather.",
    )

    requirements.add(
        name="weather",
        description="Get weather information.",
    )

    engine = RequirementDecisionEngine()

    decision = engine.decide(requirements)

    payload = decision.to_dict()

    assert payload == {
        "action": "continue",
        "reason": (
            "Some goal requirements are still "
            "pending and execution should continue."
        ),
    }


def test_replan_decision_can_be_serialized():

    requirements = GoalRequirements(
        goal="Get weather.",
    )

    requirements.add(
        name="weather",
        description="Get weather information.",
    )

    requirements.fail("weather")

    engine = RequirementDecisionEngine()

    decision = engine.decide(requirements)

    payload = decision.to_dict()

    assert payload == {
        "action": "replan",
        "reason": (
            "One or more goal requirements "
            "failed and require a different "
            "execution strategy."
        ),
    }