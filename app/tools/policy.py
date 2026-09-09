class ToolExecutionPolicy:

    def __init__(
        self,
        max_tool_calls: int = 8,
        max_iterations: int = 5,
    ):
        self.max_tool_calls = max_tool_calls
        self.max_iterations = max_iterations

    def check_tool_call(
        self,
        total_calls: int,
    ) -> None:

        if total_calls >= self.max_tool_calls:
            raise RuntimeError(
                "Maximum tool calls exceeded."
            )

    def check_iteration(
        self,
        iteration: int,
    ) -> None:

        if iteration >= self.max_iterations:
            raise RuntimeError(
                "Maximum tool iterations exceeded."
            )