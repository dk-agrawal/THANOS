from dataclasses import dataclass


@dataclass(frozen=True)
class PlanStep:
    tool_name: str
    reason: str
    depends_on: tuple[str, ...] = ()

    def __post_init__(self):
        if not self.tool_name.strip():
            raise ValueError(
                "Plan step tool name cannot be empty."
            )

        if not self.reason.strip():
            raise ValueError(
                "Plan step reason cannot be empty."
            )

        if self.tool_name in self.depends_on:
            raise ValueError(
                "A plan step cannot depend on itself."
            )

        if len(self.depends_on) != len(set(self.depends_on)):
            raise ValueError(
                "Plan step dependencies must be unique."
            )

        for dependency in self.depends_on:
            if not dependency.strip():
                raise ValueError(
                    "Plan step dependency cannot be empty."
                )

    def to_dict(self) -> dict:
        return {
            "tool_name": self.tool_name,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class ExecutionPlan:
    steps: tuple[PlanStep, ...]

    def __post_init__(self):
        step_names = {
            step.tool_name
            for step in self.steps
        }

        if len(step_names) != len(self.steps):
            raise ValueError(
                "Plan step names must be unique."
            )

        for step in self.steps:
            for dependency in step.depends_on:
                if dependency not in step_names:
                    raise ValueError(
                        "Plan step depends on an unknown "
                        f"step: {dependency}."
                    )

    @property
    def dependency_graph(self) -> dict[str, tuple[str, ...]]:
        return {
            step.tool_name: step.depends_on
            for step in self.steps
        }

    @property
    def execution_layers(self) -> tuple[tuple[str, ...], ...]:
        if not self.steps:
            return ()

        completed = set()

        remaining = {
            step.tool_name: step
            for step in self.steps
        }

        layers = []

        while remaining:
            current_layer = []

            for tool_name, step in remaining.items():
                if all(
                    dependency in completed
                    for dependency in step.depends_on
                ):
                    current_layer.append(tool_name)

            if not current_layer:
                raise ValueError(
                    "Execution plan contains a dependency cycle."
                )

            current_layer = tuple(current_layer)
            layers.append(current_layer)

            for tool_name in current_layer:
                completed.add(tool_name)
                del remaining[tool_name]

        return tuple(layers)

    def validate(self) -> None:
        if self.is_empty:
            raise ValueError(
                "Execution plan cannot be empty."
            )

        self.execution_layers

    def to_dict(self) -> dict:
        return {
            "steps": [
                step.to_dict()
                for step in self.steps
            ]
        }

    @property
    def is_empty(self) -> bool:
        return not self.steps


class ThanosPlanner:

    EXECUTION_ORDER = (
        "calculation",
        "research",
        "tool",
    )

    def create_plan(
        self,
        user_input: str,
        request_types: tuple,
    ) -> ExecutionPlan:

        text = user_input.strip()

        if not text:
            raise ValueError(
                "User input cannot be empty."
            )

        steps = []

        normalized_types = {
            getattr(
                request_type,
                "value",
                request_type,
            )
            for request_type in request_types
        }

        for request_type in self.EXECUTION_ORDER:

            if request_type not in normalized_types:
                continue

            if request_type == "calculation":

                steps.append(
                    PlanStep(
                        tool_name="calculator",
                        reason=(
                            "The user request requires "
                            "a calculation."
                        ),
                        depends_on=(),
                    )
                )

            elif request_type == "research":

                dependencies = ()

                if steps:
                    dependencies = (
                        steps[-1].tool_name,
                    )

                steps.append(
                    PlanStep(
                        tool_name="research",
                        reason=(
                            "The user request requires "
                            "research."
                        ),
                        depends_on=dependencies,
                    )
                )

            elif request_type == "tool":

                dependencies = ()

                if steps:
                    dependencies = (
                        steps[-1].tool_name,
                    )

                steps.append(
                    PlanStep(
                        tool_name="dynamic",
                        reason=(
                            "The user request requires "
                            "an external tool."
                        ),
                        depends_on=dependencies,
                    )
                )

        return ExecutionPlan(
            steps=tuple(steps)
        )

    def _get_aborted_tools(
        self,
        planning_context: dict | None,
    ) -> set[str]:

        if not planning_context:
            return set()

        tools = planning_context.get(
            "tools",
            {}
        )

        if not isinstance(tools, dict):
            return set()

        aborted_tools = set()

        for tool_name, tool_context in tools.items():

            if not isinstance(tool_context, dict):
                continue

            aborts = tool_context.get(
                "aborts",
                0
            )

            if isinstance(aborts, int) and aborts > 0:
                aborted_tools.add(tool_name)

        return aborted_tools

    def replan(
        self,
        user_input: str,
        request_types: tuple,
        failed_tool: str,
        planning_context: dict | None = None,
    ) -> ExecutionPlan:

        if not user_input.strip():
            raise ValueError(
                "User input cannot be empty."
            )

        if not failed_tool.strip():
            raise ValueError(
                "Failed tool cannot be empty."
            )

        original_plan = self.create_plan(
            user_input=user_input,
            request_types=request_types,
        )

        aborted_tools = self._get_aborted_tools(
            planning_context
        )

        blocked_tools = (
            aborted_tools
            | {failed_tool}
        )

        remaining_steps = tuple(
            step
            for step in original_plan.steps
            if step.tool_name not in blocked_tools
        )

        rebuilt_steps = []

        for step in remaining_steps:

            dependencies = tuple(
                dependency
                for dependency in step.depends_on
                if dependency not in blocked_tools
            )

            rebuilt_steps.append(
                PlanStep(
                    tool_name=step.tool_name,
                    reason=(
                        f"Replanned after '{failed_tool}' "
                        f"failed. Original reason: "
                        f"{step.reason}"
                    ),
                    depends_on=dependencies,
                )
            )

        plan = ExecutionPlan(
            steps=tuple(rebuilt_steps)
        )

        if not plan.is_empty:
            plan.validate()

        return plan