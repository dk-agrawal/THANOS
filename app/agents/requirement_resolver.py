
from dataclasses import dataclass

from app.agents.goal_requirements import (
    GoalRequirements,
    GoalRequirement,
    RequirementStatus,
)


@dataclass(frozen=True)
class RequirementResolution:
    requirement: GoalRequirement | None
    reason: str

    @property
    def found(self) -> bool:
        return self.requirement is not None

    def to_dict(self) -> dict:
        return {
            "found": self.found,
            "requirement": (
                self.requirement.to_dict()
                if self.requirement is not None
                else None
            ),
            "reason": self.reason,
        }


class RequirementResolver:

    def resolve(
        self,
        requirements: GoalRequirements,
    ) -> RequirementResolution:

        if not isinstance(requirements, GoalRequirements):
            raise ValueError(
                "Invalid goal requirements."
            )

        # Prioritize pending work before considering
        # requirements that previously failed.
        for requirement in requirements.requirements:
            if requirement.status == RequirementStatus.PENDING:
                return RequirementResolution(
                    requirement=requirement,
                    reason=(
                        "Selected the next pending "
                        "goal requirement."
                    ),
                )

        # Failed requirements need recovery or replanning.
        for requirement in requirements.requirements:
            if requirement.status == RequirementStatus.FAILED:
                return RequirementResolution(
                    requirement=requirement,
                    reason=(
                        "No pending requirements remain; "
                        "a failed requirement needs recovery."
                    ),
                )

        return RequirementResolution(
            requirement=None,
            reason=(
                "No pending or failed requirements remain."
            ),
        )
