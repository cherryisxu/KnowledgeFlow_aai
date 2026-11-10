from agent.schemas import ToolResult


def test_tool_result_success():
    result = ToolResult(
        success=True,
        data={"message": "Hello Agent"}
    )

    assert result.success is True
    assert result.data["message"] == "Hello Agent"
    assert result.error is None


def test_tool_result_failure():
    result = ToolResult(
        success=False,
        error="Something went wrong"
    )

    assert result.success is False
    assert result.error == "Something went wrong"