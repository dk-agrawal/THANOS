from app.ai.registry import AIProviderRegistry
from app.api.registry import APIRegistry

from app.core.config import settings
from app.core.update_manager import UpdateManager

from app.memory.aliases import MemoryAliasRegistry
from app.memory.history import MemoryHistory
from app.memory.long_term import LongTermMemory
from app.memory.pending import PendingMemoryStore
from app.memory.service import MemoryService

from app.tools.registry import ToolRegistry
from app.tools.system import SystemInfoTool
from app.tools.calculator import CalculatorTool

from app.tools.memory import (
    RememberTool,
    RecallTool,
    ForgetTool,
    ListMemoryTool,
)

from app.tools.pending_memory import (
    ListPendingMemoryTool,
    ConfirmPendingMemoryTool,
)

from app.tools.memory_history import (
    MemoryHistoryTool,
)

from app.tools.external.weather import WeatherTool
from app.tools.external.news import NewsTool
from app.tools.external.github import GitHubTool

from app.tools.research import ResearchTool

from app.tools.update import (
    CheckForUpdateTool,
    UpdateThanosTool,
)


def create_api_registry() -> APIRegistry:
    return APIRegistry()


def create_memory_service() -> MemoryService:

    history = MemoryHistory()

    long_term_memory = LongTermMemory(
        history=history
    )

    pending_store = PendingMemoryStore()

    return MemoryService(
        memory=long_term_memory,
        pending_store=pending_store,
        history=history,
    )


def create_memory_aliases() -> MemoryAliasRegistry:
    return MemoryAliasRegistry()


def create_update_manager() -> UpdateManager:
    return UpdateManager()


def create_tool_registry(
    api_registry: APIRegistry,
    ai_registry: AIProviderRegistry,
    memory_service: MemoryService | None = None,
    update_manager: UpdateManager | None = None,
) -> ToolRegistry:

    registry = ToolRegistry()

    registry.register(
        SystemInfoTool()
    )

    registry.register(
        CalculatorTool()
    )

    registry.register(
        WeatherTool(api_registry)
    )

    registry.register(
        NewsTool(api_registry)
    )

    registry.register(
        GitHubTool(api_registry)
    )

    registry.register(
        ResearchTool(
            registry,
            ai_registry,
        )
    )

    service = (
        memory_service
        or create_memory_service()
    )

    registry.register(
        RememberTool(
            service
        )
    )

    registry.register(
        RecallTool(
            service
        )
    )

    registry.register(
        ForgetTool(
            service
        )
    )

    registry.register(
        ListMemoryTool(
            service
        )
    )

    registry.register(
        ListPendingMemoryTool(
            service
        )
    )

    registry.register(
        ConfirmPendingMemoryTool(
            service
        )
    )

    registry.register(
        MemoryHistoryTool(
            service
        )
    )

    updater = (
        update_manager
        or create_update_manager()
    )

    if (
        settings.GITHUB_OWNER
        and settings.GITHUB_REPO
    ):

        registry.register(
            CheckForUpdateTool(
                update_manager=updater,
                owner=settings.GITHUB_OWNER,
                repo=settings.GITHUB_REPO,
            )
        )

        registry.register(
            UpdateThanosTool(
                update_manager=updater,
                owner=settings.GITHUB_OWNER,
                repo=settings.GITHUB_REPO,
                project_root=settings.PROJECT_ROOT,
            )
        )

    return registry