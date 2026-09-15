import asyncio
import json

from app.ai.registry import AIProviderRegistry
from app.ai.router import AIRouter
from app.ai.classifier import AIRequestClassifier
from app.ai.request import AIRequest, RequestType

from app.agents.planner import ExecutionPlan, ThanosPlanner
from app.agents.research_tools import ResearchToolSelector
from app.agents.tool_selector import IntelligentToolSelector

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

        self.last_request: AIRequest | None = None
        self.last_plan: ExecutionPlan | None = None

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
                        selected_names.add(tool_name)

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

        try:

            arguments = json.loads(
                arguments_raw
            )

        except json.JSONDecodeError as error:

            return {
                "tool_call_id": tool_call["id"],
                "content": json.dumps(
                    {
                        "success": False,
                        "error": (
                            "Invalid tool arguments: "
                            f"{error}"
                        ),
                    }
                ),
            }

        result = (
            await self.tool_executor.execute(
                tool_name=tool_name,
                arguments=arguments,
            )
        )

        return {
            "tool_call_id": tool_call["id"],
            "content": json.dumps(
                result.to_dict(),
                default=str,
            ),
        }

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

            results = await asyncio.gather(
                *[
                    self._execute_tool_call(
                        tool_call
                    )
                    for tool_call in tool_calls
                ]
            )

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

            response = (
                await self.ai_router.generate_with_tools(
                    messages=messages,
                    tools=tools,
                    provider_name=provider,
                )
            )
