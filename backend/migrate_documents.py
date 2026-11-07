
import shutil
import uuid
from pathlib import Path

from database import (
    init_db,
    get_connection,
    get_or_create_default_knowledge_base,
)
from text_splitter import chunk_text


BASE_DIR = Path(__file__).resolve().parent
DOCUMENTS_DIR = BASE_DIR / "documents"
UPLOADS_DIR = BASE_DIR / "uploads"


def migrate_documents():
    init_db()
    UPLOADS_DIR.mkdir(exist_ok=True)

    knowledge_base = get_or_create_default_knowledge_base()
    knowledge_base_id = knowledge_base["id"]

    migrated_count = 0

    for file_path in DOCUMENTS_DIR.iterdir():

        if not file_path.is_file():
            continue

        if file_path.suffix.lower() not in {".txt", ".md"}:
            continue

        # 读取原始文件
        content = file_path.read_text(encoding="utf-8-sig")

        if not content.strip():
            print(f"跳过空文件：{file_path.name}")
            continue

        # 文本切分
        text_chunks = chunk_text(content)

        if not text_chunks:
            print(f"切分结果为空，跳过：{file_path.name}")
            continue

        # 检查是否已经迁移过
        with get_connection() as conn:
            existing = conn.execute(
                """
                SELECT id FROM documents
                WHERE knowledge_base_id = ? AND filename = ?
                """,
                (knowledge_base_id, file_path.name),
            ).fetchone()

        if existing:
            print(f"已经迁移，跳过：{file_path.name}")
            continue

        # 使用唯一文件名保存，避免重名
        stored_name = f"{uuid.uuid4().hex}{file_path.suffix.lower()}"
        destination = UPLOADS_DIR / stored_name

        shutil.copy2(file_path, destination)

        try:
            with get_connection() as conn:

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
                        file_path.name,
                        str(destination),
                        file_path.suffix.lower().lstrip("."),
                        "completed",
                        len(text_chunks),
                    ),
                )

                document_id = cursor.lastrowid

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
                        (document_id, index, chunk)
                        for index, chunk in enumerate(
                            text_chunks, start=1
                        )
                    ],
                )

            migrated_count += 1
            print(
                f"迁移成功：{file_path.name}，"
                f"生成 {len(text_chunks)} 个 Chunks"
            )

        except Exception:
            destination.unlink(missing_ok=True)
            raise

    print(f"\n迁移完成，本次迁移 {migrated_count} 份文档")


if __name__ == "__main__":
    migrate_documents()
