from typing import Any
from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    """统一的工具执行结果"""

    success: bool
    data: Any = None
    error: str | None = None


class LLMToolCall(BaseModel):
    """模型请求执行的工具"""

    id: str
    name: str
    arguments: dict[str, Any]


class LLMResponse(BaseModel):
    """统一的模型响应"""

    content: str | None = None
    tool_calls: list[LLMToolCall] = Field(default_factory=list)
    finish_reason: str | None = None