
from fastapi import FastAPI
from pydantic import BaseModel, Field

from bm25_retriever import BM25Retriever

app = FastAPI(title="KnowledgeFlow AI")

# 暂时使用测试数据，后面再替换成真实知识库
chunks = [
    {
        "chunk_id": "chunk_001",
        "content": "Python 列表可以使用 append 添加元素。",
        "source": "python_basics.md",
    },
    {
        "chunk_id": "chunk_002",
        "content": "Python 字典使用键值对保存数据。",
        "source": "python_basics.md",
    },
    {
        "chunk_id": "chunk_003",
        "content": "红烧肉可以先煸炒，再加入调料炖煮。",
        "source": "recipes.md",
    },
]

# 服务启动时初始化一次，后续请求复用检索器
retriever = BM25Retriever(chunks)


class RetrieveRequest(BaseModel):
    query: str = Field(min_length=1, description="用户的问题")
    top_k: int = Field(default=3, ge=1, le=10)


@app.get("/")
def home():
    return {"message": "KnowledgeFlow AI API is running"}


@app.post("/retrieve")
def retrieve(request: RetrieveRequest):
    results = retriever.retrieve(
        query=request.query,
        top_k=request.top_k,
    )

    return {
        "query": request.query,
        "count": len(results),
        "results": results,
    }
