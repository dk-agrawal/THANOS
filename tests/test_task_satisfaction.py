from app.agents.task_satisfaction import (
    TaskSatisfactionAction,
    TaskSatisfactionEngine,
)


def test_complete_result():

    engine = TaskSatisfactionEngine()

    decision = engine.evaluate(
        tool_name="weather",
        result={
            "temperature": 28,
            "humidity": 60,
        },
    )

    assert (
        decision.action
        == TaskSatisfactionAction.COMPLETE
    )

    assert decision.tool_name == "weather"


def test_missing_result_is_unsatisfied():

    engine = TaskSatisfactionEngine()

    decision = engine.evaluate(
        tool_name="weather",
        result=None,
    )

    assert (
        decision.action
        == TaskSatisfactionAction.UNSATISFIED
    )


def test_empty_result_is_unsatisfied():

    engine = TaskSatisfactionEngine()

    decision = engine.evaluate(
        tool_name="weather",
        result={},
    )

    assert (
        decision.action
        == TaskSatisfactionAction.UNSATISFIED
    )


def test_missing_required_fields_is_partial():

    engine = TaskSatisfactionEngine()

    decision = engine.evaluate(
        tool_name="weather",
        result={
            "temperature": 28,
        },
        required_fields={
            "temperature",
            "humidity",
        },
    )

    assert (
        decision.action
        == TaskSatisfactionAction.PARTIAL
    )

    assert "humidity" in decision.reason


def test_all_required_fields_is_complete():

    engine = TaskSatisfactionEngine()

    decision = engine.evaluate(
        tool_name="weather",
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
        decision.action
        == TaskSatisfactionAction.COMPLETE
    )


def test_unstructured_result_with_required_fields_is_unsatisfied():

    engine = TaskSatisfactionEngine()

    decision = engine.evaluate(
        tool_name="weather",
        result="28 degrees",
        required_fields={
            "temperature",
        },
    )

    assert (
        decision.action
        == TaskSatisfactionAction.UNSATISFIED
    )


def test_empty_tool_name_is_rejected():

    engine = TaskSatisfactionEngine()

    try:
        engine.evaluate(
            tool_name="",
            result={
                "temperature": 28,
            },
        )
    except ValueError as error:
        assert str(error) == "Tool name cannot be empty."
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_decision_can_be_serialized():

    engine = TaskSatisfactionEngine()

    decision = engine.evaluate(
        tool_name="weather",
        result={
            "temperature": 28,
        },
    )

    payload = decision.to_dict()

    assert payload == {
        "action": "complete",
        "tool_name": "weather",
        "reason": (
            "The tool produced a result "
            "that satisfies the available "
            "requirements."
        ),
    }