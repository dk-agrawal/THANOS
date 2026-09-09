import asyncio

from app.ai.registry import AIProviderRegistry
from app.agents.agent import ThanosAgent
from app.core.bootstrap import (
    create_api_registry,
    create_memory_aliases,
    create_tool_registry,
)


async def main():

    print("=" * 50)
    print("THANOS AI")
    print("Agent online")
    print("=" * 50)

    api_registry = create_api_registry()

    ai_registry = AIProviderRegistry()

    tool_registry = create_tool_registry(
        api_registry,
        ai_registry,
    )

    memory_aliases = create_memory_aliases()

    agent = ThanosAgent(
        ai_registry=ai_registry,
        tool_registry=tool_registry,
        memory_aliases=memory_aliases,
    )

    while True:

        try:

            user_input = input(
                "\nYou: "
            ).strip()

            if not user_input:
                continue

            if user_input.lower() in {
                "exit",
                "quit",
            }:

                print(
                    "THANOS: Goodbye."
                )

                break

            response = await agent.handle(
                user_input
            )

            print(
                f"THANOS: {response}"
            )

        except KeyboardInterrupt:

            print(
                "\nTHANOS: Goodbye."
            )

            break

        except Exception as error:

            print(
                f"THANOS ERROR: {error}"
            )


if __name__ == "__main__":
    asyncio.run(main())