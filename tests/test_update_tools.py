import asyncio

from app.tools.update import (
    CheckForUpdateTool,
    UpdateThanosTool,
)


class FakeUpdateManager:

    async def check_for_update(
        self,
        owner,
        repo,
    ):

        return {
            "success": True,
            "update_available": True,
            "update": {
                "current_version": "0.1.0",
                "latest_version": "0.2.0",
            },
        }

    async def update(
        self,
        owner,
        repo,
        project_root,
        dry_run=True,
    ):

        return {
            "success": True,
            "updated": True,
            "dry_run": dry_run,
            "message": (
                "THANOS update completed successfully."
            ),
        }


def test_check_for_update_tool():

    tool = CheckForUpdateTool(
        update_manager=FakeUpdateManager(),
        owner="example",
        repo="thanos",
    )

    result = asyncio.run(
        tool.execute()
    )

    assert result.success is True

    assert (
        result.data[
            "update_available"
        ]
        is True
    )


def test_check_tool_definition():

    tool = CheckForUpdateTool(
        update_manager=FakeUpdateManager(),
        owner="example",
        repo="thanos",
    )

    definition = tool.definition()

    assert (
        definition["function"]["name"]
        == "check_for_update"
    )

    assert (
        definition["function"]["parameters"][
            "type"
        ]
        == "object"
    )


def test_update_requires_confirmation():

    tool = UpdateThanosTool(
        update_manager=FakeUpdateManager(),
        owner="example",
        repo="thanos",
        project_root="project",
    )

    result = asyncio.run(
        tool.execute(
            confirm=False
        )
    )

    assert result.success is False

    assert (
        "not authorized"
        in result.error.lower()
    )


def test_update_with_confirmation():

    tool = UpdateThanosTool(
        update_manager=FakeUpdateManager(),
        owner="example",
        repo="thanos",
        project_root="project",
    )

    result = asyncio.run(
        tool.execute(
            confirm=True
        )
    )

    assert result.success is True

    assert (
        result.data["updated"]
        is True
    )


def test_update_tool_definition():

    tool = UpdateThanosTool(
        update_manager=FakeUpdateManager(),
        owner="example",
        repo="thanos",
        project_root="project",
    )

    definition = tool.definition()

    assert (
        definition["function"]["name"]
        == "update_thanos"
    )

    parameters = (
        definition["function"]["parameters"]
    )

    assert "confirm" in (
        parameters["properties"]
    )

    assert (
        "confirm"
        in parameters["required"]
    )