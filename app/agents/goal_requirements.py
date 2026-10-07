from dataclasses import dataclass, field
from enum import Enum


class RequirementStatus(str, Enum):
    PENDING = "pending"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class GoalRequirement:
    name: str
    description: str
    status: RequirementStatus = RequirementStatus.PENDING

    def complete(self) -> None:
        self.status = RequirementStatus.COMPLETE

    def fail(self) -> None:
        self.status = RequirementStatus.FAILED

    @property
    def is_complete(self) -> bool:
        return self.status == RequirementStatus.COMPLETE

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "is_complete": self.is_complete,
        }


@dataclass
class GoalRequirements:
    goal: str
    requirements: list[GoalRequirement] = field(
        default_factory=list
    )

    def add(
        self,
        name: str,
        description: str,
    ) -> GoalRequirement:

        if not name.strip():
            raise ValueError(
                "Requirement name cannot be empty."
            )

        if not description.strip():
            raise ValueError(
                "Requirement description cannot be empty."
            )

        requirement = GoalRequirement(
            name=name,
            description=description,
        )

        self.requirements.append(requirement)

        return requirement

    def get(
        self,
        name: str,
    ) -> GoalRequirement | None:

        for requirement in self.requirements:
            if requirement.name == name:
                return requirement

        return None

    def complete(
        self,
        name: str,
    ) -> bool:

        requirement = self.get(name)

        if requirement is None:
            return False

        requirement.complete()
        return True

    def fail(
        self,
        name: str,
    ) -> bool:

        requirement = self.get(name)

        if requirement is None:
            return False

        requirement.fail()
        return True

    @property
    def pending(self) -> list[GoalRequirement]:
        return [
            requirement
            for requirement in self.requirements
            if requirement.status
            == RequirementStatus.PENDING
        ]

    @property
    def completed(self) -> list[GoalRequirement]:
        return [
            requirement
            for requirement in self.requirements
            if requirement.status
            == RequirementStatus.COMPLETE
        ]

    @property
    def failed(self) -> list[GoalRequirement]:
        return [
            requirement
            for requirement in self.requirements
            if requirement.status
            == RequirementStatus.FAILED
        ]

    @property
    def is_complete(self) -> bool:
        return (
            bool(self.requirements)
            and not self.pending
            and not self.failed
        )

    def to_dict(self) -> dict:
        return {
            "goal": self.goal,
            "requirements": [
                requirement.to_dict()
                for requirement in self.requirements
            ],
            "pending": [
                requirement.name
                for requirement in self.pending
            ],
            "completed": [
                requirement.name
                for requirement in self.completed
            ],
            "failed": [
                requirement.name
                for requirement in self.failed
            ],
            "is_complete": self.is_complete,
        }