
from dataclasses import dataclass

from app.agents.goal_requirements import (
    GoalRequirements,
)
from app.agents.requirement_resolver import (
    RequirementResolver,
)


@dataclass(frozen=True)
class RequirementContext:
    goal: str
    target_name: str
    target_description: str
    pending_requirements: tuple[str, ...]
    completed_requirements: tuple[str, ...]
    failed_requirements: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "goal": self.goal,
            "target": {
                "name": self.target_name,
                "description": self.target_description,
            },
            "pending_requirements": list(
                self.pending_requirements
            ),
            "completed_requirements": list(
                self.completed_requirements
            ),
            "failed_requirements": list(
                self.failed_requirements
            ),
        }


class RequirementContextBuilder:

    def __init__(
        self,
        resolver: RequirementResolver | None = None,
    ):
        self.resolver = resolver or RequirementResolver()

    def build(
        self,
        requirements: GoalRequirements,
    ) -> RequirementContext | None:

        if not isinstance(requirements, GoalRequirements):
            raise ValueError(
                "Invalid goal requirements."
            )

        resolution = self.resolver.resolve(requirements)

        if not resolution.found:
            return None

        target = resolution.requirement

        return RequirementContext(
            goal=requirements.goal,
            target_name=target.name,
            target_description=target.description,
            pending_requirements=tuple(
                requirement.name
                for requirement in requirements.pending
            ),
            completed_requirements=tuple(
                requirement.name
                for requirement in requirements.completed
            ),
            failed_requirements=tuple(
                requirement.name
                for requirement in requirements.failed
            ),
        )
