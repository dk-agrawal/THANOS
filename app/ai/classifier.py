from app.ai.request import AIRequest, RequestType


class AIRequestClassifier:

    def classify(
        self,
        user_input: str,
    ) -> AIRequest:

        text = user_input.strip()

        if not text:
            raise ValueError(
                "User input cannot be empty."
            )

        request_type = self._detect_type(
            text
        )

        return AIRequest(
            user_input=text,
            request_type=request_type,
        )

    def _detect_type(
        self,
        text: str,
    ) -> RequestType:

        normalized = text.lower()

        if self._is_calculation(
            normalized
        ):
            return RequestType.CALCULATION

        if self._is_research(
            normalized
        ):
            return RequestType.RESEARCH

        if self._is_tool_request(
            normalized
        ):
            return RequestType.TOOL

        return RequestType.CHAT

    @staticmethod
    def _is_calculation(
        text: str,
    ) -> bool:

        calculation_keywords = {
            "calculate",
            "calculation",
            "solve",
            "compute",
        }

        if any(
            keyword in text
            for keyword in calculation_keywords
        ):
            return True

        operators = (
            "+",
            "-",
            "*",
            "/",
            "%",
        )

        return any(
            operator in text
            for operator in operators
        )

    @staticmethod
    def _is_research(
        text: str,
    ) -> bool:

        research_keywords = {
            "research",
            "analyze",
            "analysis",
            "deep research",
            "investigate",
            "compare",
            "latest news",
        }

        return any(
            keyword in text
            for keyword in research_keywords
        )

    @staticmethod
    def _is_tool_request(
        text: str,
    ) -> bool:

        tool_keywords = {
            "weather",
            "github",
            "remember",
            "recall",
            "forget",
            "system information",
            "system info",
        }

        return any(
            keyword in text
            for keyword in tool_keywords
        )