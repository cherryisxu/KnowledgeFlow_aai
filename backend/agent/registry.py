from agent.base import BaseTool


class ToolRegistry:
    """工具注册中心"""

    def __init__(self):
        self.tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        if tool.name in self.tools:
            raise ValueError(f"Tool already registered: {tool.name}")

        self.tools[tool.name] = tool

    def get(self, name: str) -> BaseTool | None:
        return self.tools.get(name)

    def list_tools(self) -> list[BaseTool]:
        return list(self.tools.values())