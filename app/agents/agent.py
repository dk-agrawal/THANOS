import json

from app.ai.registry import AIProviderRegistry
from app.ai.router import AIRouter

from app.core.intent import IntentDetector, IntentType

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

        self.tool_registry = tool_registry

        self.tool_executor = ToolExecutor(
            tool_registry
        )

        self.intent_detector = IntentDetector()

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

    async def handle(
        self,
        user_input: str,
    ) -> str:

        self.memory.add_user_message(
            user_input
        )

        self.memory_pipeline.process(
            user_input
        )

        intent = self.intent_detector.detect(
            user_input
        )

        if intent == IntentType.CALCULATION:

            tools = self._get_calculation_tools()

        else:

            tools = (
                self.tool_registry.definitions()
            )

        return await self._run_tool_loop(
            user_input=user_input,
            tools=tools,
        )

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

    async def _run_tool_loop(
        self,
        user_input: str,
        tools: list[dict],
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

            for tool_call in tool_calls:

                self.policy.check_tool_call(
                    total_tool_calls
                )

                total_tool_calls += 1

                function = (
                    tool_call["function"]
                )

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

                    result = {
                        "success": False,
                        "error": (
                            "Invalid tool arguments: "
                            f"{error}"
                        ),
                    }

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": (
                                tool_call["id"]
                            ),
                            "content": json.dumps(
                                result
                            ),
                        }
                    )

                    continue

                result = (
                    await self.tool_executor.execute(
                        tool_name=tool_name,
                        arguments=arguments,
                    )
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": (
                            tool_call["id"]
                        ),
                        "content": json.dumps(
                            result.to_dict(),
                            default=str,
                        ),
                    }
                )

            response = (
                await self.ai_router.generate_with_tools(
                    messages=messages,
                    tools=tools,
                )
            )