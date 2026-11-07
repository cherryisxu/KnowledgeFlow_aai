
import sqlite3
from pathlib import Path

# 当前 backend 目录
BASE_DIR = Path(__file__).resolve().parent

# 数据库存放位置
DATABASE_PATH = BASE_DIR / "knowledgeflow.db"


def get_connection():
    """创建数据库连接"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """初始化数据库和数据表"""

    with get_connection() as conn:

        # 1. 知识库表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_bases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. 文档表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                knowledge_base_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_type TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                chunk_count INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (knowledge_base_id)
                REFERENCES knowledge_bases(id)
                ON DELETE CASCADE
            )
        """)

        # 3. 文档分块表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER NOT NULL,
                chunk_index INTEGER NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (document_id)
                REFERENCES documents(id)
                ON DELETE CASCADE
            )
        """)

        # 建立索引，方便根据文档查询 Chunk
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_chunks_document_id
            ON chunks(document_id)
        """)

        conn.commit()


def get_or_create_default_knowledge_base():
    """获取默认知识库，如果不存在则创建"""

    with get_connection() as conn:
        row = conn.execute("""
            SELECT id, name
            FROM knowledge_bases
            WHERE name = ?
        """, ("KnowledgeFlow 默认知识库",)).fetchone()

        if row:
            return dict(row)

        cursor = conn.execute("""
            INSERT INTO knowledge_bases (name, description)
            VALUES (?, ?)
        """, (
            "KnowledgeFlow 默认知识库",
            "KnowledgeFlow AI 的默认知识资料库"
        ))

        return {
            "id": cursor.lastrowid,
            "name": "KnowledgeFlow 默认知识库"
        }



def get_completed_chunks():
    """获取所有已完成文档的 Chunk，供 BM25 重建索引使用"""

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT
                c.document_id,
                c.chunk_index,
                c.content,
                d.filename
            FROM chunks AS c
            JOIN documents AS d
                ON c.document_id = d.id
            WHERE d.status = 'completed'
            ORDER BY d.id, c.chunk_index
        """).fetchall()

    results = []

    for row in rows:
        results.append({
            "chunk_id": f"doc{row['document_id']}_{row['chunk_index']:03d}",
            "content": row["content"],
            "source": row["filename"],
        })

    return results


def save_document_with_chunks(
    filename: str,
    file_path: str,
    file_type: str,
    chunks: list[str],
    knowledge_base_id: int,
):
    """
    保存文档及其 Chunks。

    文档记录和 Chunk 记录使用同一个数据库事务。
    如果操作失败，自动回滚。
    """

    if not filename.strip():
        raise ValueError("文件名不能为空")

    if not chunks:
        raise ValueError("文档没有可保存的 Chunks")

    with get_connection() as conn:

        # 开启写事务，避免并发上传时重复文件名
        conn.execute("BEGIN IMMEDIATE")

        # 检查同一知识库中是否存在同名文件
        existing = conn.execute(
            """
            SELECT id
            FROM documents
            WHERE knowledge_base_id = ?
            AND filename = ?
            """,
            (knowledge_base_id, filename),
        ).fetchone()

        if existing:
            raise ValueError("该文件已经存在，请勿重复上传")

        # 1. 保存文档信息
        cursor = conn.execute(
            """
            INSERT INTO documents (
                knowledge_base_id,
                filename,
                file_path,
                file_type,
                status,
                chunk_count
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                knowledge_base_id,
                filename,
                file_path,
                file_type,
                "completed",
                len(chunks),
            ),
        )

        document_id = cursor.lastrowid

        # 2. 保存所有 Chunks
        conn.executemany(
            """
            INSERT INTO chunks (
                document_id,
                chunk_index,
                content
            )
            VALUES (?, ?, ?)
            """,
            [
                (document_id, index, content)
                for index, content in enumerate(chunks, start=1)
            ],
        )

        return {
            "document_id": document_id,
            "filename": filename,
            "status": "completed",
            "chunk_count": len(chunks),
        }

