
from document_loader import load_documents
from text_splitter import chunk_text
from database import get_completed_chunks


def build_chunks_from_db() -> list[dict[str, str]]:
    """
    从 SQLite 数据库读取已完成文档的 Chunks，
    供 BM25 检索器构建索引。
    """
    chunks = get_completed_chunks()

    return chunks


def build_chunks() -> list[dict[str, str]]:
    documents = load_documents()
    chunks = []

    for document in documents:
        text_chunks = chunk_text(document["content"])

        for index, content in enumerate(text_chunks, start=1):
            chunks.append({
                "chunk_id": f"{document['source']}_{index:03d}",
                "content": content,
                "source": document["source"],
            })

    return chunks


if __name__ == "__main__":
    chunks = build_chunks()

    print(f"共生成 {len(chunks)} 个 chunks")

    for chunk in chunks:
        print(f"\nID：{chunk['chunk_id']}")
        print(f"来源：{chunk['source']}")
        print(f"长度：{len(chunk['content'])}")
        print(chunk["content"][:80])
