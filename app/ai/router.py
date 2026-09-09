from enum import Enum

class TaskType(Enum):
    SIMPLE = "simple"
    GENERAL = "general"
    COMPLEX = "complex"


class AIRouter:

    def classify(self, prompt: str) -> TaskType:
        prompt = prompt.lower().strip()

        if len(prompt) < 40:
            return TaskType.SIMPLE

        if any(
            keyword in prompt
            for keyword in [
                "analyze",
                "explain deeply",
                "compare",
                "design",
                "debug",
                "arcitecture",
                "research",
            ]
        ):
            return TaskType.COMPLEX
        return TaskType.GENERAL