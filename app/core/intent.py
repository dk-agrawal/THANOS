from enum import Enum


class IntentType(Enum):
    GENERAL = "general"
    CALCULATION = "calculation"


class IntentDetector:

    def detect(self, text: str) -> IntentType:
        text = text.lower().strip()

        calculation_symbols = [
            "+",
            "-",
            "*",
            "/",
            "%",
        ]

        if any(symbol in text for symbol in calculation_symbols):
            return IntentType.CALCULATION

        calculation_words = [
            "calculate",
            "calcuate",
            "add",
            "subtract",
            "multiply",
            "divide",
        ]

        if any(word in text for word in calculation_words):
            return IntentType.CALCULATION

        return IntentType.GENERAL