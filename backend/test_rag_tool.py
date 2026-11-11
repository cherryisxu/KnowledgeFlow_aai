from main import retriever
from agent.tools.rag_tool import RAGTool
from agent.registry import ToolRegistry
from agent.agent import Agent

# 1. 创建 RAGTool
rag_tool = RAGTool(retriever)

# 2. 注册工具
registry = ToolRegistry()
registry.register(rag_tool)

# 3. 创建 Agent
agent = Agent(registry)

# # 4. 通过 Agent 调用工具
# result = agent.execute_tool(
#     tool_name="rag_search",
#     arguments={
#         "query": "Python 列表如何增加元素？",
#         "top_k": 3
#     }
# )

# definitions = agent.get_tool_definitions()

# print(definitions)

# response = agent.think(
#     "Python 列表如何增加元素？"
# )

# print("LLM Response:")
# print(response.model_dump())
# 1. 让 LLM 自主选择工具
# response = agent.think(
#     "Python 列表如何增加元素？"
# )

# print("LLM Response:")
# print(response.model_dump())

# # 2. Agent 自动执行工具
# results = agent.execute_tool_calls(response)

# print("Tool Execution Results:")
# print(results)

# 4. 通过 Agent 统一入口执行
# result = agent.run(
#     "Python 列表如何增加元素？"
# )
result = agent.run(
    "linux 系统中如何查看当前目录下的所有文件和文件夹？"
)
# result = agent.run(
#     "请介绍一下你自己"
# )

print("Agent Final Answer:")
print(result)