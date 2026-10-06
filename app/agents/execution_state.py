from dataclasses import dataclass, field
from enum import Enum


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class ToolExecutionState:
    tool_name: str
    layer_index: int
    status: ExecutionStatus = ExecutionStatus.PENDING
    error: str | None = None

    def start(self) -> None:
        self.status = ExecutionStatus.RUNNING
        self.error = None

    def succeed(self) -> None:
        self.status = ExecutionStatus.SUCCESS
        self.error = None

    def fail(self, error: str) -> None:
        self.status = ExecutionStatus.FAILED
        self.error = error

    def to_dict(self) -> dict:
        return {
            "tool_name": self.tool_name,
            "layer_index": self.layer_index,
            "status": self.status.value,
            "error": self.error,
        }


@dataclass
class ExecutionState:
    tools: dict[str, ToolExecutionState] = field(
        default_factory=dict
    )

    def register(
        self,
        tool_name: str,
        layer_index: int,
    ) -> ToolExecutionState:

        if tool_name in self.tools:
            raise ValueError(
                f"Tool already registered: {tool_name}"
            )

        state = ToolExecutionState(
            tool_name=tool_name,
            layer_index=layer_index,
        )

        self.tools[tool_name] = state

        return state

    def get(
        self,
        tool_name: str,
    ) -> ToolExecutionState | None:

        return self.tools.get(tool_name)

    def start(
        self,
        tool_name: str,
    ) -> None:

        state = self._require(tool_name)
        state.start()

    def succeed(
        self,
        tool_name: str,
    ) -> None:

        state = self._require(tool_name)
        state.succeed()

    def fail(
        self,
        tool_name: str,
        error: str,
    ) -> None:

        state = self._require(tool_name)
        state.fail(error)

    def completed_tools(self) -> tuple[str, ...]:

        return tuple(
            tool_name
            for tool_name, state in self.tools.items()
            if state.status == ExecutionStatus.SUCCESS
        )

    def failed_tools(self) -> tuple[str, ...]:

        return tuple(
            tool_name
            for tool_name, state in self.tools.items()
            if state.status == ExecutionStatus.FAILED
        )

    def pending_tools(self) -> tuple[str, ...]:

        return tuple(
            tool_name
            for tool_name, state in self.tools.items()
            if state.status == ExecutionStatus.PENDING
        )

    def is_complete(self) -> bool:

        if not self.tools:
            return True

        return all(
            state.status
            in {
                ExecutionStatus.SUCCESS,
                ExecutionStatus.FAILED,
            }
            for state in self.tools.values()
        )

    def to_dict(self) -> dict:

        return {
            "tools": {
                tool_name: state.to_dict()
                for tool_name, state in self.tools.items()
            },
            "completed": list(
                self.completed_tools()
            ),
            "failed": list(
                self.failed_tools()
            ),
            "pending": list(
                self.pending_tools()
            ),
            "complete": self.is_complete(),
        }

    def _require(
        self,
        tool_name: str,
    ) -> ToolExecutionState:

        state = self.get(tool_name)

        if state is None:
            raise ValueError(
                f"Tool is not registered: {tool_name}"
            )

        return state