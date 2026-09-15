from dataclasses import dataclass


@dataclass(frozen=True)
class PlanStep:

    tool_name: str
    reason: str

    def to_dict(self) -> dict:

        return {
            "tool_name": self.tool_name,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class ExecutionPlan:

    steps: tuple[PlanStep, ...]

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

    def create_plan(
        self,
        request_types: tuple,
    ) -> ExecutionPlan:

        steps = []

        if self._contains(
            request_types,
            "calculation",
        ):
            steps.append(
                PlanStep(
                    tool_name="calculator",
                    reason="The request requires calculation.",
                )
            )

        if self._contains(
            request_types,
            "research",
        ):
            steps.append(
                PlanStep(
                    tool_name="research",
                    reason="The request requires research.",
                )
            )

        if self._contains(
            request_types,
            "tool",
        ):
            steps.append(
                PlanStep(
                    tool_name="dynamic",
                    reason="The request requires an external tool.",
                )
            )

        return ExecutionPlan(
            steps=tuple(steps)
        )

    @staticmethod
    def _contains(
        request_types: tuple,
        value: str,
    ) -> bool:

        for request_type in request_types:

            if getattr(
                request_type,
                "value",
                request_type,
            ) == value:

                return True

        return False
