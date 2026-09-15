from app.agents.planner import (
    ExecutionPlan,
    PlanStep,
    ThanosPlanner,
)


def test_planner_creates_calculation_plan():

    planner = ThanosPlanner()

    plan = planner.create_plan(
        ("calculation",)
    )

    assert isinstance(
        plan,
        ExecutionPlan,
    )

    assert len(plan.steps) == 1

    assert plan.steps[0] == PlanStep(
        tool_name="calculator",
        reason="The request requires calculation.",
    )


def test_planner_creates_research_plan():

    planner = ThanosPlanner()

    plan = planner.create_plan(
        ("research",)
    )

    assert len(plan.steps) == 1

    assert plan.steps[0].tool_name == (
        "research"
    )


def test_planner_creates_multi_intent_plan():

    planner = ThanosPlanner()

    plan = planner.create_plan(
        (
            "calculation",
            "research",
        )
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
        ("tool",)
    )

    assert len(plan.steps) == 1

    assert plan.steps[0].tool_name == (
        "dynamic"
    )


def test_planner_returns_empty_plan_for_chat():

    planner = ThanosPlanner()

    plan = planner.create_plan(
        ("chat",)
    )

    assert plan.is_empty is True

    assert plan.steps == ()


def test_execution_plan_to_dict():

    plan = ExecutionPlan(
        steps=(
            PlanStep(
                tool_name="calculator",
                reason="The request requires calculation.",
            ),
            PlanStep(
                tool_name="research",
                reason="The request requires research.",
            ),
        )
    )

    assert plan.to_dict() == {
        "steps": [
            {
                "tool_name": "calculator",
                "reason": (
                    "The request requires calculation."
                ),
            },
            {
                "tool_name": "research",
                "reason": (
                    "The request requires research."
                ),
            },
        ]
    }


def test_plan_step_to_dict():

    step = PlanStep(
        tool_name="calculator",
        reason="The request requires calculation.",
    )

    assert step.to_dict() == {
        "tool_name": "calculator",
        "reason": (
            "The request requires calculation."
        ),
    }


def test_planner_accepts_request_type_objects():

    from app.ai.request import RequestType

    planner = ThanosPlanner()

    plan = planner.create_plan(
        (
            RequestType.CALCULATION,
            RequestType.RESEARCH,
        )
    )

    assert [
        step.tool_name
        for step in plan.steps
    ] == [
        "calculator",
        "research",
    ]
