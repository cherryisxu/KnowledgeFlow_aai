from agent.registry import ToolRegistry
from llm_service import llm_service
from agent.schemas import ToolResult, LLMResponse
import json


class Agent:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def execute_tool(
        self,
        tool_name: str,
        arguments: dict
    ) -> ToolResult:

        # 1. 根据名称获取工具
        tool = self.registry.get(tool_name)

        # 2. 如果工具不存在
        if not tool:
            return ToolResult(
                success=False,
                error=f"Tool '{tool_name}' not found."
            )

        # 3. 调用工具
        try:
            result = tool.execute(**arguments)
            return result

        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Tool execution failed: {str(e)}"
            )
        
    def get_tool_definitions(self):
        tools = self.registry.list_tools()

        definitions = []

        for tool in tools:
            definition = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                } 
            }
            definitions.append(definition)

        return definitions

    def think(self, user_input: str):
        messages = [
            {
                "role": "system",
               "content": "你是一个知识库问答助手。当用户询问知识性问题时，优先使用 rag_search 工具检索知识库。"
            },
            {
               "role": "user",
               "content": user_input
           }
        ]

        response = llm_service.chat(
            messages=messages,
           tools=self.get_tool_definitions()
        )

        return response, messages

    def execute_tool_calls(
        self,
        response: LLMResponse
    ):
        results = []

        for tool_call in response.tool_calls:

            # 1. 获取工具名称和参数
            tool_name = tool_call.name
            arguments = tool_call.arguments

            # 2. 执行工具
            result = self.execute_tool(
                tool_name=tool_name,
                arguments=arguments
            )

            # 3. 保存执行结果
            results.append({
                "tool_call_id": tool_call.id,
                "name": tool_name,
                "result": result.model_dump()
            })

        return results

    def build_tool_messages(self, response, results):
        messages = []

        # 这里需要构建 assistant 的工具调用消息
        assistant_message = {
            "role": "assistant",
            "content": None,
            "tool_calls": []
        }

        # 这里需要构建每个 tool 的执行结果消息
        for tool_call in response.tool_calls:
            assistant_message["tool_calls"].append({
                "id": tool_call.id,
                "type": "function",
                "function": {
                    "name": tool_call.name,
                    "arguments": json.dumps(tool_call.arguments, ensure_ascii=False)
                }
            })

        messages.append(assistant_message)

        for item in results:
            # 在这里构建 tool_message
            tool_message = {
            # 这里补充三个字段
            "role": "tool",
            "tool_call_id": item["tool_call_id"],
            "content": json.dumps(item["result"], ensure_ascii=False)
            }
            messages.append(tool_message)

        return messages 

    def run(self, user_input: str):
        # 第一步：让 LLM 思考
        response, messages = self.think(user_input)
        print("------------------------")
        print("LLM Tool Calls:")
        print([call.name for call in response.tool_calls])
        # 第二步：如果没有工具调用，直接返回回答
        if not response.tool_calls:
            return response.content
        # 第三步：执行工具调用
        results = self.execute_tool_calls(response)
        print("------------------------")
        print("Tool Results:")
        print(results)
        # 第四步：构建工具消息
        tool_messages = self.build_tool_messages(response, results)
        # 把工具消息追加到原来的 messages
        messages.extend(tool_messages)

        # 再次调用 LLM，生成最终回答
        final_response = llm_service.chat(
            messages=messages
        )

        return final_response.content