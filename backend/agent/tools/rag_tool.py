
from agent.base import BaseTool
from agent.schemas import ToolResult
from bm25_retriever import BM25Retriever


class RAGTool(BaseTool):
    name = "rag_search"
    description = "根据用户问题检索知识库中的相关内容"
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "用户提出的问题"
            },
            "top_k": {
                "type": "integer",
                "description": "返回的相关知识片段数量，默认3"
            }
        },
        "required": ["query"],
        "additionalProperties": False
    }


    def __init__(self, retriever: BM25Retriever):
        self.retriever = retriever

    def execute(self, **kwargs) -> ToolResult:
        # 1. 获取参数
        query = kwargs.get("query")
        top_k = kwargs.get("top_k", 3)

        # 2. 参数校验
        if not isinstance(query, str) or not query.strip():
            return ToolResult(
                success=False,
                error="无效的 query 参数"
            )

        if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k <= 0:
            return ToolResult(
                success=False,
                error="top_k 必须是正整数"
            )

        # 3. 执行检索
        try:
            results = self.retriever.retrieve(
                query=query,
                top_k=top_k
            )

            return ToolResult(
                success=True,
                data=results
            )

        except Exception as e:
            return ToolResult(
                success=False,
                error=f"RAG 检索失败：{str(e)}"
            )
    
