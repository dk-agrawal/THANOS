import asyncio
import json

from app.agents.recovery import RecoveryEngine, RecoveryAction
from app.ai.registry import AIProviderRegistry
from app.ai.router import AIRouter
from app.ai.classifier import AIRequestClassifier
from app.ai.request import AIRequest, RequestType

from app.agents.planner import ExecutionPlan, ThanosPlanner
from app.agents.research_tools import ResearchToolSelector
from app.agents.tool_selector import IntelligentToolSelector
from app.agents.execution_state import ExecutionState
from app.agents.execution_history import ExecutionHistory
from app.agents.result_decision import ResultDecisionEngine

from app.tools.executor import ToolExecutor
from app.tools.registry import ToolRegistry
from app.tools.policy import ToolExecutionPolicy

from app.memory.manager import MemoryManager
from app.memory.long_term import LongTermMemory
from app.memory.pipeline import MemoryPipeline
from app.memory.retrieval import MemoryRetriever
from app.memory.aliases import MemoryAliasRegistry


class ThanosAgent:

    def __init__(
        self,
        ai_registry: AIProviderRegistry,
        tool_registry: ToolRegistry,
        memory: MemoryManager | None = None,
        long_term_memory: LongTermMemory | None = None,
        memory_aliases: MemoryAliasRegistry | None = None,
    ):
        self.ai_registry = ai_registry

        self.ai_router = AIRouter(
            registry=ai_registry,
            default_provider="openrouter",
        )

        self.request_classifier = (
            AIRequestClassifier()
        )

        self.planner = ThanosPlanner()

        self.tool_registry = tool_registry

        self.tool_executor = ToolExecutor(
            tool_registry
        )

        self.policy = ToolExecutionPolicy()

        self.memory = (
            memory or MemoryManager()
        )

        self.long_term_memory = (
            long_term_memory
            or LongTermMemory()
        )

        self.memory_pipeline = MemoryPipeline(
            memory=self.long_term_memory
        )

        self.memory_aliases = (
            memory_aliases
            or MemoryAliasRegistry()
        )

        self.memory_retriever = MemoryRetriever(
            memory=self.long_term_memory,
            aliases=self.memory_aliases,
        )

        self.research_tool_selector = (
            ResearchToolSelector(
                tool_registry
            )
        )

        self.tool_selector = (
            IntelligentToolSelector(
                tool_registry
            )
        )
        self.recovery_engine = RecoveryEngine()
        self.result_decision_engine = ResultDecisionEngine()
        self.last_request: AIRequest | None = None
        self.last_plan: ExecutionPlan | None = None
        self.last_execution_state: ExecutionState | None = None
        self.last_execution_history: ExecutionHistory | None = None

    async def handle(
        self,
        user_input: str,
    ) -> str:

        request = (
            self.request_classifier.classify(
                user_input
            )
        )

        self.last_request = request

        self.memory.add_user_message(
            request.user_input
        )

        self.memory_pipeline.process(
            request.user_input
        )

        decision = self.ai_router.decide(
            request_type=request.request_type,
            provider=request.provider,
            request_types=request.request_types,
        )

        plan = self.planner.create_plan(
            request.user_input,
            request.request_types,
        )

        self.last_plan = plan

        self.last_execution_state = (
            self._create_execution_state(plan)
        )
        self.last_execution_history = ExecutionHistory()

        tools = self._select_tools(
            request=request,
            plan=plan,
            use_tools=decision.use_tools,
            use_research=decision.use_research,
        )

        return await self._run_tool_loop(
            user_input=request.user_input,
            tools=tools,
            provider=decision.provider,
        )

    def _create_execution_state(
        self,
        plan: ExecutionPlan,
    ) -> ExecutionState:

        state = ExecutionState()

        for layer_index, layer in enumerate(
            plan.execution_layers
        ):
            for tool_name in layer:
                state.register(
                    tool_name=tool_name,
                    layer_index=layer_index,
                )

        return state

    def _select_tools(
        self,
        request: AIRequest,
        plan: ExecutionPlan | None = None,
        use_tools: bool = False,
        use_research: bool = False,
    ) -> list[dict]:

        if not use_tools:
            return []

        if plan is None:
            plan = self.planner.create_plan(
                request.user_input,
                request.request_types,
            )

        planned_tools = {
            step.tool_name
            for step in plan.steps
        }

        selected_tools = []
        selected_names = set()

        request_types = request.request_types

        if (
            use_research
            and "research" in planned_tools
        ):
            research_tools = (
                self.research_tool_selector.select()
            )

            for tool in research_tools:

                tool_name = (
                    tool["function"]["name"]
                )

                if tool_name not in selected_names:
                    selected_tools.append(tool)
                    selected_names.add(tool_name)

        if (
            RequestType.CALCULATION in request_types
            and "calculator" in planned_tools
        ):

            calculator = (
                self.tool_registry.get(
                    "calculator"
                )
            )

            if calculator is not None:

                tool_definition = (
                    calculator.definition()
                )

                tool_name = (
                    tool_definition["function"]["name"]
                )

                if tool_name not in selected_names:
                    selected_tools.append(
                        tool_definition
                    )
                    selected_names.add(
                        tool_name
                    )

        if RequestType.TOOL in request_types:

            intelligent_tools = (
                self.tool_selector.select(
                    request.user_input
                )
            )

            for tool in intelligent_tools:

                tool_name = (
                    tool["function"]["name"]
                )

                if (
                    "dynamic" in planned_tools
                    or tool_name in planned_tools
                ):
                    if tool_name not in selected_names:
                        selected_tools.append(tool)
                        selected_names.add(
                            tool_name
                        )

        if not selected_tools:
            return self.tool_registry.definitions()

        return selected_tools

    def _get_calculation_tools(
        self,
    ) -> list[dict]:

        calculator = self.tool_registry.get(
            "calculator"
        )

        if calculator is None:
            raise RuntimeError(
                "Calculator tool is not registered"
            )

        return [
            calculator.definition()
        ]

    def _build_messages(
        self,
        user_input: str,
    ) -> list[dict]:

        messages = []

        relevant_memory = (
            self.memory_retriever.get_context(
                query=user_input,
                limit=5,
            )
        )

        if relevant_memory:
            messages.append(
                {
                    "role": "system",
                    "content": (
                        "You are THANOS AI.\n\n"
                        "Use the following relevant "
                        "long-term memories when "
                        "answering the user.\n\n"
                        f"{relevant_memory}"
                    ),
                }
            )

        messages.extend(
            self.memory.get_context()
        )

        return messages

    def _get_tool_plan_layer(
        self,
        tool_name: str,
        plan: ExecutionPlan | None,
    ) -> int | None:

        if plan is None:
            return None

        for layer_index, layer in enumerate(
            plan.execution_layers
        ):

            if tool_name in layer:
                return layer_index

            if "dynamic" in layer:
                if (
                    tool_name != "research"
                    and self.tool_registry.get(
                        tool_name
                    ) is not None
                ):
                    return layer_index

        return None

    def _record_execution_event(
        self,
        tool_name: str,
        status: str,
        retry_count: int = 0,
        recovery_action: str | None = None,
        error: str | None = None,
        result: object | None = None,
    ) -> None:

        if self.last_execution_history is None:
            return

        layer_index = self._get_tool_plan_layer(
            tool_name=tool_name,
            plan=self.last_plan,
        )

        if layer_index is None:
            layer_index = -1

        self.last_execution_history.record(
            tool_name=tool_name,
            layer_index=layer_index,
            status=status,
            retry_count=retry_count,
            recovery_action=recovery_action,
            error=error,
            result=result,
        )

    async def _execute_tool_call(
        self,
        tool_call: dict,
    ) -> dict:

        function = tool_call["function"]
        tool_name = function["name"]

        arguments_raw = function.get(
            "arguments",
            "{}",
        )

        if self.last_execution_state is not None:
            state = self.last_execution_state.get(
                tool_name
            )

            if state is not None:
                self.last_execution_state.start(
                    tool_name
                )

        try:
            arguments = json.loads(arguments_raw)
        except json.JSONDecodeError as error:
            error_message = f"Invalid tool arguments: {error}"

            if self.last_execution_state is not None:
                state = self.last_execution_state.get(tool_name)
                if state is not None:
                    self.last_execution_state.fail(
                        tool_name,
                        error_message,
                    )

            self._record_execution_event(
                tool_name=tool_name,
                status="failed",
                error=error_message,
            )

            return {
                "tool_call_id": tool_call["id"],
                "content": json.dumps({
                    "success": False,
                    "error": error_message,
                }),
            }

        retry_count = 0
        max_retries = self.tool_executor.max_retries

        while True:
            try:
                result = await self.tool_executor.execute_once(
                    tool_name=tool_name,
                    arguments=arguments,
                )

                result_decision = self.result_decision_engine.decide(
                    tool_name=tool_name,
                    success=result.success,
                    result=result.data,
                    error=result.error,
                )

                recovery_decision = self.recovery_engine.decide(
                    tool_name=tool_name,
                    result=result,
                    retry_count=retry_count,
                    max_retries=max_retries,
                    history=self.last_execution_history,
                )

                if recovery_decision.action == RecoveryAction.RETRY:
                    self._record_execution_event(
                        tool_name=tool_name,
                        status="failed",
                        retry_count=retry_count,
                        recovery_action=recovery_decision.action.value,
                        error=result.error,
                    )
                    retry_count += 1
                    continue

                if self.last_execution_state is not None:
                    state = self.last_execution_state.get(tool_name)
                    if state is not None:
                        if result.success:
                            self.last_execution_state.succeed(tool_name)
                        else:
                            self.last_execution_state.fail(
                                tool_name,
                                result.error or "Tool execution failed.",
                            )

                self._record_execution_event(
                    tool_name=tool_name,
                    status=(
                        "success"
                        if result.success
                        else "failed"
                    ),
                    retry_count=retry_count,
                    recovery_action=recovery_decision.action.value,
                    error=(
                        None
                        if result.success
                        else result.error
                    ),
                    result=result.data,
                )

                result_payload = result.to_dict()
                result_payload["recovery"] = recovery_decision.to_dict()
                result_payload["attempts"] = retry_count + 1

                return {
                    "tool_call_id": tool_call["id"],
                    "content": json.dumps(
                        result_payload,
                        default=str,
                    ),
                }

            except Exception as error:
                error_message = f"{type(error).__name__}: {error}"
                failure_result = {
                    "success": False,
                    "error": error_message,
                }

                if self.last_execution_state is not None:
                    state = self.last_execution_state.get(tool_name)
                    if state is not None:
                        self.last_execution_state.fail(
                            tool_name,
                            error_message,
                        )

                self._record_execution_event(
                    tool_name=tool_name,
                    status="failed",
                    retry_count=retry_count,
                    error=error_message,
                )

                return {
                    "tool_call_id": tool_call["id"],
                    "content": json.dumps(failure_result),
                }

    def _get_replanned_tools(
        self,
        tools: list[dict],
        plan: ExecutionPlan,
        failed_tool: str,
    ) -> list[dict]:

        planned_tools = {
            step.tool_name
            for step in plan.steps
        }

        if not planned_tools:
            return []

        selected_tools = []

        for tool in tools:
            function = tool.get("function", {})
            tool_name = function.get("name")

            if not tool_name or tool_name == failed_tool:
                continue

            if "dynamic" in planned_tools:
                selected_tools.append(tool)
                continue

            if tool_name in planned_tools:
                selected_tools.append(tool)

        return selected_tools

    def _replan_after_failure(
        self,
        user_input: str,
        tools: list[dict],
        failed_tool: str,
    ) -> list[dict]:

        if self.last_request is None:
            return tools

        planning_context = None

        if self.last_execution_history is not None:
            planning_context = (
                self.last_execution_history.planning_context()
            )

            result_context = (
                self.last_execution_history.result_context()
            )

            planning_context = {
                **planning_context,
                "results": result_context,
            }

        new_plan = self.planner.replan(
            user_input=user_input,
            request_types=self.last_request.request_types,
            failed_tool=failed_tool,
            planning_context=planning_context,
        )

        self.last_plan = new_plan
        self.last_execution_state = (
            self._create_execution_state(new_plan)
        )

        return self._get_replanned_tools(
            tools=tools,
            plan=new_plan,
            failed_tool=failed_tool,
        )

    async def _execute_tool_calls_by_plan(
        self,
        tool_calls: list[dict],
    ) -> list[dict]:

        plan = self.last_plan

        if plan is None:
            return await asyncio.gather(
                *[
                    self._execute_tool_call(
                        tool_call
                    )
                    for tool_call in tool_calls
                ]
            )

        grouped_calls: dict[int, list[dict]] = {}
        unplanned_calls = []

        for tool_call in tool_calls:

            tool_name = (
                tool_call["function"]["name"]
            )

            layer_index = (
                self._get_tool_plan_layer(
                    tool_name=tool_name,
                    plan=plan,
                )
            )

            if layer_index is None:
                unplanned_calls.append(
                    tool_call
                )
                continue

            grouped_calls.setdefault(
                layer_index,
                [],
            ).append(tool_call)

        results = []

        for layer_index in sorted(
            grouped_calls
        ):

            layer_calls = (
                grouped_calls[layer_index]
            )

            layer_results = await asyncio.gather(
                *[
                    self._execute_tool_call(
                        tool_call
                    )
                    for tool_call in layer_calls
                ]
            )

            results.extend(
                layer_results
            )

        if unplanned_calls:

            unplanned_results = await asyncio.gather(
                *[
                    self._execute_tool_call(
                        tool_call
                    )
                    for tool_call in unplanned_calls
                ]
            )

            results.extend(
                unplanned_results
            )

        return results

    async def _run_tool_loop(
        self,
        user_input: str,
        tools: list[dict],
        provider: str,
    ) -> str:

        iteration = 0
        total_tool_calls = 0

        messages = self._build_messages(
            user_input
        )

        response = (
            await self.ai_router.generate_with_tools(
                messages=messages,
                tools=tools,
                provider_name=provider,
            )
        )

        while True:

            self.policy.check_iteration(
                iteration
            )

            iteration += 1

            assistant_message = (
                response["choices"][0]["message"]
            )

            tool_calls = (
                assistant_message.get(
                    "tool_calls"
                )
            )

            if not tool_calls:

                final_response = (
                    assistant_message.get(
                        "content",
                        "",
                    )
                )

                self.memory.add_assistant_message(
                    final_response
                )

                return final_response

            messages.append(
                assistant_message
            )

            for _ in tool_calls:

                self.policy.check_tool_call(
                    total_tool_calls
                )

                total_tool_calls += 1

            results = (
                await self._execute_tool_calls_by_plan(
                    tool_calls
                )
            )

            replan_tool = None

            for result in results:

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": (
                            result["tool_call_id"]
                        ),
                        "content": result["content"],
                    }
                )

                try:
                    result_payload = json.loads(
                        result["content"]
                    )
                except (
                    TypeError,
                    json.JSONDecodeError,
                ):
                    result_payload = {}

                recovery = result_payload.get(
                    "recovery"
                )

                if (
                    isinstance(recovery, dict)
                    and recovery.get("action")
                    == RecoveryAction.ABORT.value
                ):
                    abort_reason = recovery.get(
                        "reason",
                        "Recovery was aborted.",
                    )

                    final_response = (
                        "THANOS stopped the operation safely. "
                        f"Recovery reason: {abort_reason}"
                    )

                    self.memory.add_assistant_message(
                        final_response
                    )

                    return final_response

                if (
                    isinstance(recovery, dict)
                    and recovery.get("action")
                    == RecoveryAction.REPLAN.value
                ):
                    replan_tool = recovery.get(
                        "tool_name"
                    )
                    break

            if replan_tool:
                tools = self._replan_after_failure(
                    user_input=user_input,
                    tools=tools,
                    failed_tool=replan_tool,
                )

                # If replanning leaves THANOS with no viable tools,
                # stop the tool loop instead of continuing with an
                # empty tool set and risking meaningless execution.
                if not tools:
                    final_response = (
                        "THANOS could not continue the operation "
                        "because the failed tool could not be replaced "
                        "with a viable remaining tool."
                    )

                    self.memory.add_assistant_message(
                        final_response
                    )

                    return final_response

            response = (
                await self.ai_router.generate_with_tools(
                    messages=messages,
                    tools=tools,
                    provider_name=provider,
                )
            )
