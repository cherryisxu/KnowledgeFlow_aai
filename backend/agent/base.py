from abc import ABC, abstractmethod
from agent.schemas import ToolResult


class BaseTool(ABC):
    """所有 Agent 工具的基础类"""

    name: str = ""
    description: str = ""

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """执行工具"""
        pass