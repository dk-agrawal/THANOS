import pytest
from app.agents.planner import (
    ExecutionPlan,
    PlanStep,
    ThanosPlanner,
)


def test_planner_creates_calculation_plan():

    planner = ThanosPlanner()

    plan = planner.create_plan(
        "Calculate 25 * 8",
        ("calculation",),
    )

    assert isinstance(
        plan,
        ExecutionPlan,
    )

    assert len(plan.steps) == 1

    assert plan.steps[0] == PlanStep(
        tool_name="calculator",
        reason=(
            "The user request requires "
            "a calculation."
        ),
    )


def test_planner_creates_research_plan():

    planner = ThanosPlanner()

    plan = planner.create_plan(
        "Research the latest AI news",
        ("research",),
    )

    assert len(plan.steps) == 1

    assert plan.steps[0].tool_name == (
        "research"
    )


def test_planner_creates_multi_intent_plan():

    planner = ThanosPlanner()

    plan = planner.create_plan(
        "Calculate 25 * 8 and research latest AI news",
        (
            "calculation",
            "research",
        ),
    )

    assert len(plan.steps) == 2

    assert [
        step.tool_name
        for step in plan.steps
    ] == [
        "calculator",
        "research",
    ]


def test_planner_creates_tool_plan():

    planner = ThanosPlanner()

    plan = planner.create_plan(
        "Check the weather",
        ("tool",),
    )

    assert len(plan.steps) == 1

    assert plan.steps[0].tool_name == (
        "dynamic"
    )


def test_planner_returns_empty_plan_for_chat():

    planner = ThanosPlanner()

    plan = planner.create_plan(
        "Hello THANOS",
        ("chat",),
    )

    assert plan.is_empty is True

    assert plan.steps == ()


def test_execution_plan_to_dict():

    plan = ExecutionPlan(
        steps=(
            PlanStep(
                tool_name="calculator",
                reason=(
                    "The user request requires "
                    "a calculation."
                ),
            ),
            PlanStep(
                tool_name="research",
                reason=(
                    "The user request requires "
                    "research."
                ),
            ),
        )
    )

    assert plan.to_dict() == {
        "steps": [
            {
                "tool_name": "calculator",
                "reason": (
                    "The user request requires "
                    "a calculation."
                ),
            },
            {
                "tool_name": "research",
                "reason": (
                    "The user request requires "
                    "research."
                ),
            },
        ]
    }


def test_plan_step_to_dict():

    step = PlanStep(
        tool_name="calculator",
        reason=(
            "The user request requires "
            "a calculation."
        ),
    )

    assert step.to_dict() == {
        "tool_name": "calculator",
        "reason": (
            "The user request requires "
            "a calculation."
        ),
    }


def test_planner_accepts_request_type_objects():

    from app.ai.request import RequestType

    planner = ThanosPlanner()

    plan = planner.create_plan(
        "Calculate 25 * 8 and research latest AI news",
        (
            RequestType.CALCULATION,
            RequestType.RESEARCH,
        ),
    )

    assert [
        step.tool_name
        for step in plan.steps
    ] == [
        "calculator",
        "research",
    ]


def test_planner_rejects_empty_user_input():

    planner = ThanosPlanner()

    try:
        planner.create_plan(
            "",
            ("calculation",),
        )
    except ValueError as error:
        assert str(error) == (
            "User input cannot be empty."
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_planner_preserves_execution_order():

    planner = ThanosPlanner()

    plan = planner.create_plan(
        "Calculate 25 * 8 and research latest AI news",
        (
            "calculation",
            "research",
        ),
    )

    assert [
        step.tool_name
        for step in plan.steps
    ] == [
        "calculator",
        "research",
    ]

    assert [
        step.reason
        for step in plan.steps
    ] == [
        "The user request requires a calculation.",
        "The user request requires research.",
    ]


def test_planner_supports_step_dependencies():

    planner = ThanosPlanner()

    plan = planner.create_plan(
        "Research AI news and then calculate the result",
        (
            "research",
            "calculation",
        ),
    )

    assert len(plan.steps) == 2

    assert plan.steps[0].tool_name == "calculator"
    assert plan.steps[1].tool_name == "research"

    assert plan.steps[0].depends_on == ()
    assert plan.steps[1].depends_on == ("calculator",)


def test_plan_step_rejects_self_dependency():

    try:
        PlanStep(
            tool_name="calculator",
            reason="Calculation",
            depends_on=("calculator",),
        )
    except ValueError as error:
        assert str(error) == (
            "A plan step cannot depend on itself."
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_plan_step_rejects_duplicate_dependencies():

    try:
        PlanStep(
            tool_name="research",
            reason="Research",
            depends_on=(
                "calculator",
                "calculator",
            ),
        )
    except ValueError as error:
        assert str(error) == (
            "Plan step dependencies must be unique."
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_plan_step_rejects_empty_dependency_name():

    try:
        PlanStep(
            tool_name="research",
            reason="Research",
            depends_on=("",),
        )
    except ValueError as error:
        assert str(error) == (
            "Plan step dependency cannot be empty."
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_execution_plan_rejects_unknown_dependency():

    try:
        ExecutionPlan(
            steps=(
                PlanStep(
                    tool_name="calculator",
                    reason="Calculation",
                ),
                PlanStep(
                    tool_name="research",
                    reason="Research",
                    depends_on=("github",),
                ),
            )
        )
    except ValueError as error:
        assert str(error) == (
            "Plan step depends on an unknown step: github."
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_execution_plan_builds_dependency_graph():

    plan = ExecutionPlan(
        steps=(
            PlanStep(
                tool_name="calculator",
                reason="Calculation",
            ),
            PlanStep(
                tool_name="research",
                reason="Research",
                depends_on=("calculator",),
            ),
            PlanStep(
                tool_name="dynamic",
                reason="External tool",
                depends_on=("research",),
            ),
        )
    )

    assert plan.dependency_graph == {
        "calculator": (),
        "research": ("calculator",),
        "dynamic": ("research",),
    }


def test_execution_plan_builds_execution_layers():

    plan = ExecutionPlan(
        steps=(
            PlanStep(
                tool_name="calculator",
                reason="Calculation",
            ),
            PlanStep(
                tool_name="weather",
                reason="Weather",
            ),
            PlanStep(
                tool_name="research",
                reason="Research",
                depends_on=("calculator",),
            ),
            PlanStep(
                tool_name="dynamic",
                reason="External tool",
                depends_on=("research", "weather"),
            ),
        )
    )

    assert plan.execution_layers == (
        ("calculator", "weather"),
        ("research",),
        ("dynamic",),
    )

def test_replan_removes_failed_tool():
    planner = ThanosPlanner()

    plan = planner.replan(
        user_input="calculate something and research it",
        request_types=(
            "calculation",
            "research",
        ),
        failed_tool="calculator",
    )

    assert [step.tool_name for step in plan.steps] == [
        "research"
    ]


def test_replan_removes_failed_dependency():
    planner = ThanosPlanner()

    plan = planner.replan(
        user_input="calculate something and research it",
        request_types=(
            "calculation",
            "research",
        ),
        failed_tool="calculator",
    )

    assert plan.dependency_graph["research"] == ()


def test_replan_preserves_unrelated_steps():
    planner = ThanosPlanner()

    plan = planner.replan(
        user_input="calculate and research",
        request_types=(
            "calculation",
            "research",
        ),
        failed_tool="unknown_tool",
    )

    assert [step.tool_name for step in plan.steps] == [
        "calculator",
        "research",
    ]


def test_replan_rejects_empty_input():
    planner = ThanosPlanner()

    with pytest.raises(ValueError):
        planner.replan(
            user_input="",
            request_types=("research",),
            failed_tool="research",
        )


def test_replan_rejects_empty_failed_tool():
    planner = ThanosPlanner()

    with pytest.raises(ValueError):
        planner.replan(
            user_input="research something",
            request_types=("research",),
            failed_tool="",
        )

def test_execution_plan_validate_success():
    planner = ThanosPlanner()

    plan = planner.create_plan(
        user_input="calculate and research",
        request_types=(
            "calculation",
            "research",
        ),
    )

    plan.validate()


def test_execution_plan_validate_rejects_empty_plan():
    plan = ExecutionPlan(
        steps=()
    )

    with pytest.raises(ValueError):
        plan.validate()


def test_replanned_plan_is_valid():
    planner = ThanosPlanner()

    plan = planner.replan(
        user_input="calculate and research",
        request_types=(
            "calculation",
            "research",
        ),
        failed_tool="calculator",
    )

    plan.validate()

    assert plan.execution_layers == (
        ("research",),
    )


def test_replan_uses_planning_context_to_block_aborted_tools():
    planner = ThanosPlanner()

    planning_context = {
        "total_events": 3,
        "successful": 0,
        "failed": 3,
        "retries": 1,
        "replans": 1,
        "aborts": 1,
        "tools": {
            "calculator": {
                "attempts": 2,
                "successes": 0,
                "failures": 2,
                "retries": 1,
                "replans": 1,
                "aborts": 0,
                "last_status": "failed",
                "last_recovery_action": "replan",
                "last_error": "Calculator failed.",
            },
            "research": {
                "attempts": 1,
                "successes": 0,
                "failures": 1,
                "retries": 0,
                "replans": 0,
                "aborts": 1,
                "last_status": "failed",
                "last_recovery_action": "abort",
                "last_error": "Research failed.",
            },
        },
    }

    plan = planner.replan(
        user_input=(
            "Calculate something and research the latest news"
        ),
        request_types=("calculation", "research"),
        failed_tool="calculator",
        planning_context=planning_context,
    )

    assert plan.steps == ()


def test_replan_without_planning_context_preserves_old_behavior():
    planner = ThanosPlanner()

    plan = planner.replan(
        user_input=(
            "Calculate something and research the latest news"
        ),
        request_types=("calculation", "research"),
        failed_tool="calculator",
    )

    assert len(plan.steps) == 1
    assert plan.steps[0].tool_name == "research"

