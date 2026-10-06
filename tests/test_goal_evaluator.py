from app.agents.goal_evaluator import (
    GoalEvaluationAction,
    GoalEvaluator,
)


def test_goal_is_achieved():

    evaluator = GoalEvaluator()

    evaluation = evaluator.evaluate(
        goal="Get weather information",
        result={
            "temperature": 28,
            "humidity": 60,
        },
    )

    assert (
        evaluation.action
        == GoalEvaluationAction.ACHIEVED
    )

    assert evaluation.goal == "Get weather information"


def test_missing_result_means_not_achieved():

    evaluator = GoalEvaluator()

    evaluation = evaluator.evaluate(
        goal="Get weather information",
        result=None,
    )

    assert (
        evaluation.action
        == GoalEvaluationAction.NOT_ACHIEVED
    )


def test_empty_result_means_not_achieved():

    evaluator = GoalEvaluator()

    evaluation = evaluator.evaluate(
        goal="Get weather information",
        result={},
    )

    assert (
        evaluation.action
        == GoalEvaluationAction.NOT_ACHIEVED
    )


def test_missing_requirements_mean_partial():

    evaluator = GoalEvaluator()

    evaluation = evaluator.evaluate(
        goal="Get complete weather information",
        result={
            "temperature": 28,
        },
        required_fields={
            "temperature",
            "humidity",
        },
    )

    assert (
        evaluation.action
        == GoalEvaluationAction.PARTIAL
    )

    assert "humidity" in evaluation.reason


def test_all_requirements_mean_achieved():

    evaluator = GoalEvaluator()

    evaluation = evaluator.evaluate(
        goal="Get complete weather information",
        result={
            "temperature": 28,
            "humidity": 60,
        },
        required_fields={
            "temperature",
            "humidity",
        },
    )

    assert (
        evaluation.action
        == GoalEvaluationAction.ACHIEVED
    )


def test_unstructured_result_with_requirements():

    evaluator = GoalEvaluator()

    evaluation = evaluator.evaluate(
        goal="Get weather information",
        result="28 degrees",
        required_fields={
            "temperature",
        },
    )

    assert (
        evaluation.action
        == GoalEvaluationAction.NOT_ACHIEVED
    )


def test_empty_goal_is_rejected():

    evaluator = GoalEvaluator()

    try:
        evaluator.evaluate(
            goal="",
            result={
                "temperature": 28,
            },
        )
    except ValueError as error:
        assert str(error) == "Goal cannot be empty."
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_goal_evaluation_can_be_serialized():

    evaluator = GoalEvaluator()

    evaluation = evaluator.evaluate(
        goal="Get weather information",
        result={
            "temperature": 28,
        },
    )

    payload = evaluation.to_dict()

    assert payload == {
        "action": "achieved",
        "goal": "Get weather information",
        "reason": (
            "The available result satisfies "
            "the known requirements of the goal."
        ),
    }