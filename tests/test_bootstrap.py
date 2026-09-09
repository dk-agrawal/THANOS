from app.ai.registry import AIProviderRegistry
from app.api.registry import APIRegistry
from app.core.bootstrap import (
    create_tool_registry,
)
from app.tools.registry import ToolRegistry


class FakeUpdateManager:
    pass


def test_update_tools_are_registered():

    api_registry = APIRegistry()

    ai_registry = AIProviderRegistry()

    update_manager = (
        FakeUpdateManager()
    )

    registry = create_tool_registry(
        api_registry=api_registry,
        ai_registry=ai_registry,
        update_manager=update_manager,
    )

    assert isinstance(
        registry,
        ToolRegistry,
    )