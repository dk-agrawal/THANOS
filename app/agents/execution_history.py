from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionEvent:
    tool_name: str
    layer_index: int
    status: str
    retry_count: int = 0
    recovery_action: str | None = None
    error: str | None = None
    result: object | None = None

    def to_dict(self) -> dict:
        return {
            "tool_name": self.tool_name,
            "layer_index": self.layer_index,
            "status": self.status,
            "retry_count": self.retry_count,
            "recovery_action": self.recovery_action,
            "error": self.error,
            "result": self.result,
        }


class ExecutionHistory:
    def __init__(self):
        self.events: list[ExecutionEvent] = []

    def record(
        self,
        tool_name: str,
        layer_index: int,
        status: str,
        retry_count: int = 0,
        recovery_action: str | None = None,
        error: str | None = None,
        result: object | None = None,
    ) -> ExecutionEvent:
        event = ExecutionEvent(
            tool_name=tool_name,
            layer_index=layer_index,
            status=status,
            retry_count=retry_count,
            recovery_action=recovery_action,
            error=error,
            result=result,
        )
        self.events.append(event)
        return event

    def all_events(self) -> tuple[ExecutionEvent, ...]:
        return tuple(self.events)

    def tool_events(self, tool_name: str) -> tuple[ExecutionEvent, ...]:
        return tuple(
            event for event in self.events
            if event.tool_name == tool_name
        )

    def failed_events(self) -> tuple[ExecutionEvent, ...]:
        return tuple(
            event for event in self.events
            if event.status == "failed"
        )

    def successful_events(self) -> tuple[ExecutionEvent, ...]:
        return tuple(
            event for event in self.events
            if event.status == "success"
        )

    def recovery_events(self) -> tuple[ExecutionEvent, ...]:
        return tuple(
            event for event in self.events
            if event.recovery_action is not None
        )

    def replan_events(self) -> tuple[ExecutionEvent, ...]:
        return tuple(
            event for event in self.events
            if event.recovery_action == "replan"
        )

    def retry_events(self) -> tuple[ExecutionEvent, ...]:
        return tuple(
            event for event in self.events
            if event.recovery_action == "retry"
        )

    def abort_events(self) -> tuple[ExecutionEvent, ...]:
        return tuple(
            event for event in self.events
            if event.recovery_action == "abort"
        )

    def tool_recovery_events(self, tool_name: str) -> tuple[ExecutionEvent, ...]:
        return tuple(
            event for event in self.tool_events(tool_name)
            if event.recovery_action is not None
        )

    def tool_replan_events(self, tool_name: str) -> tuple[ExecutionEvent, ...]:
        return tuple(
            event for event in self.tool_events(tool_name)
            if event.recovery_action == "replan"
        )

    def tool_retry_events(self, tool_name: str) -> tuple[ExecutionEvent, ...]:
        return tuple(
            event for event in self.tool_events(tool_name)
            if event.recovery_action == "retry"
        )

    def tool_abort_events(self, tool_name: str) -> tuple[ExecutionEvent, ...]:
        return tuple(
            event for event in self.tool_events(tool_name)
            if event.recovery_action == "abort"
        )

    def tool_replan_count(self, tool_name: str) -> int:
        return len(self.tool_replan_events(tool_name))

    def tool_retry_count(self, tool_name: str) -> int:
        return len(self.tool_retry_events(tool_name))

    def tool_abort_count(self, tool_name: str) -> int:
        return len(self.tool_abort_events(tool_name))

    @property
    def replan_count(self) -> int:
        return len(self.replan_events())

    @property
    def retry_count(self) -> int:
        return len(self.retry_events())

    @property
    def abort_count(self) -> int:
        return len(self.abort_events())

    def planning_context(self) -> dict:
        tool_names = sorted({event.tool_name for event in self.events})
        tools = {}

        for tool_name in tool_names:
            events = self.tool_events(tool_name)
            last_event = events[-1] if events else None

            tools[tool_name] = {
                "attempts": len(events),
                "successes": sum(
                    event.status == "success"
                    for event in events
                ),
                "failures": sum(
                    event.status == "failed"
                    for event in events
                ),
                "retries": self.tool_retry_count(tool_name),
                "replans": self.tool_replan_count(tool_name),
                "aborts": self.tool_abort_count(tool_name),
                "last_status": (
                    last_event.status
                    if last_event
                    else None
                ),
                "last_recovery_action": (
                    last_event.recovery_action
                    if last_event
                    else None
                ),
                "last_error": (
                    last_event.error
                    if last_event
                    else None
                ),
                **(
                    {
                        "last_result": last_event.result
                    }
                    if last_event and last_event.result is not None
                    else {}
                ),
            }

        return {
            "total_events": len(self.events),
            "successful": len(self.successful_events()),
            "failed": len(self.failed_events()),
            "retries": self.retry_count,
            "replans": self.replan_count,
            "aborts": self.abort_count,
            "tools": tools,
        }

    def result_context(self) -> dict:
        """Return the latest meaningful result for each executed tool."""
        results = {}

        for tool_name in sorted({event.tool_name for event in self.events}):
            events = self.tool_events(tool_name)

            for event in reversed(events):
                if event.result is not None:
                    results[tool_name] = {
                        "status": event.status,
                        "result": event.result,
                        "error": event.error,
                        "layer_index": event.layer_index,
                    }
                    break

        return results

    def clear(self) -> None:
        self.events.clear()

    def to_dict(self) -> dict:
        return {
            "total_events": len(self.events),
            "successful": len(self.successful_events()),
            "failed": len(self.failed_events()),
            "retries": self.retry_count,
            "replans": self.replan_count,
            "aborts": self.abort_count,
            "events": [
                event.to_dict()
                for event in self.events
            ],
        }
