from pathlib import Path

from app.core.update_manager import UpdateManager
from app.tools.base import Tool
from app.tools.result import ToolResult


class CheckForUpdateTool(Tool):

    def __init__(
        self,
        update_manager: UpdateManager,
        owner: str,
        repo: str,
    ):
        self.update_manager = update_manager
        self.owner = owner
        self.repo = repo

    @property
    def name(self) -> str:
        return "check_for_update"

    @property
    def description(self) -> str:
        return (
            "Checks whether a newer THANOS version "
            "is available from the configured GitHub "
            "repository."
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {},
        }

    async def execute(
        self,
        **kwargs,
    ) -> ToolResult:

        try:

            result = (
                await self.update_manager.check_for_update(
                    owner=self.owner,
                    repo=self.repo,
                )
            )

            return ToolResult(
                success=True,
                data=result,
            )

        except Exception as error:

            return ToolResult(
                success=False,
                error=str(error),
            )


class UpdateThanosTool(Tool):

    def __init__(
        self,
        update_manager: UpdateManager,
        owner: str,
        repo: str,
        project_root: str | Path,
    ):
        self.update_manager = update_manager
        self.owner = owner
        self.repo = repo
        self.project_root = Path(
            project_root
        )

    @property
    def name(self) -> str:
        return "update_thanos"

    @property
    def description(self) -> str:
        return (
            "Updates THANOS to the latest available "
            "version. This is an explicit update "
            "operation and is not performed automatically."
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "confirm": {
                    "type": "boolean",
                    "description": (
                        "Must be true to explicitly "
                        "authorize the update."
                    ),
                }
            },
            "required": [
                "confirm",
            ],
        }

    async def execute(
        self,
        confirm: bool,
        **kwargs,
    ) -> ToolResult:

        if confirm is not True:

            return ToolResult(
                success=False,
                error=(
                    "Update not authorized. "
                    "Set confirm=true to explicitly "
                    "authorize the THANOS update."
                ),
            )

        try:

            result = (
                await self.update_manager.update(
                    owner=self.owner,
                    repo=self.repo,
                    project_root=(
                        self.project_root
                    ),
                    dry_run=False,
                )
            )

            return ToolResult(
                success=result.get(
                    "success",
                    False,
                ),
                data=result,
                error=(
                    None
                    if result.get("success")
                    else result.get(
                        "message",
                        "THANOS update failed.",
                    )
                ),
            )

        except Exception as error:

            return ToolResult(
                success=False,
                error=str(error),
            )