from agent.base import BaseTool
from agent.registry import ToolRegistry
from agent.schemas import ToolResult


class HelloTool(BaseTool):
    name = "hello"
    description = "A simple greeting tool"

    def execute(self, **kwargs) -> ToolResult:
        return ToolResult(
            success=True,
            data={"message": "Hello Agent!"}
        )


def test_register_and_get_tool():
    registry = ToolRegistry()
    tool = HelloTool()

    registry.register(tool)

    found_tool = registry.get("hello")

    assert found_tool is tool


def test_execute_tool():
    registry = ToolRegistry()
    registry.register(HelloTool())

    tool = registry.get("hello")
    result = tool.execute()

    assert result.success is True
    assert result.data["message"] == "Hello Agent!"


def test_list_tools():
    registry = ToolRegistry()
    registry.register(HelloTool())

    tools = registry.list_tools()

    assert len(tools) == 1
    assert tools[0].name == "hello"


def test_duplicate_registration():
    registry = ToolRegistry()
    registry.register(HelloTool())

    try:
        registry.register(HelloTool())
    except ValueError:
        pass
    else:
        assert False, "Expected ValueError"