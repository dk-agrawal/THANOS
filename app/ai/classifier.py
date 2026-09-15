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

        request_types = self._detect_types(
            text
        )

        primary_type = self._get_primary_type(
            request_types
        )

        return AIRequest(
            user_input=text,
            request_type=primary_type,
            request_types=tuple(
                request_types
            ),
        )

    def _detect_types(
        self,
        text: str,
    ) -> list[RequestType]:

        normalized = text.lower()

        detected = []

        if self._is_calculation(
            normalized
        ):
            detected.append(
                RequestType.CALCULATION
            )

        if self._is_research(
            normalized
        ):
            detected.append(
                RequestType.RESEARCH
            )

        if self._is_tool_request(
            normalized
        ):
            detected.append(
                RequestType.TOOL
            )

        if not detected:
            detected.append(
                RequestType.CHAT
            )

        return detected

    @staticmethod
    def _get_primary_type(
        request_types: list[RequestType],
    ) -> RequestType:

        priority = (
            RequestType.RESEARCH,
            RequestType.CALCULATION,
            RequestType.TOOL,
            RequestType.CHAT,
        )

        for request_type in priority:

            if request_type in request_types:
                return request_type

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