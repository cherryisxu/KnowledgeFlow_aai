
from knowledge_base import build_chunks
from bm25_retriever import BM25Retriever



TEST_QUERIES = [
    "Python 列表如何添加元素？",
    "Python 列表如何删除元素？",
    "红烧肉怎么做？",
]

def main():
    chunks = build_chunks()
    retriever = BM25Retriever(chunks)

    for query in TEST_QUERIES:
        print(f"\n{'=' * 50}")
        print(f"问题：{query}")

        results = retriever.retrieve(query, top_k=3)

        if not results:
            print("没有检索到结果")
            continue

        for rank, result in enumerate(results, start=1):
            print(f"\n排名：{rank}")
            print(f"分数：{result['score']:.3f}")
            print(f"分块 ID：{result['chunk_id']}")
            print(f"来源：{result['source']}")
            # print(f"内容：{result['content'][:150]}")
            print(f"内容：\n{result['content']}")
        
        

if __name__ == "__main__":
    main()
