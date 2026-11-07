
from pathlib import Path


DOCUMENTS_DIR = Path(__file__).parent / "documents"


def load_documents() -> list[dict[str, str]]:
    documents = []

    for file_path in DOCUMENTS_DIR.iterdir():
        if not file_path.is_file():
            continue

        if file_path.suffix.lower() not in {".txt", ".md"}:
            continue

        content = file_path.read_text(encoding="utf-8")

        documents.append({
            "source": file_path.name,
            "content": content,
        })

    return documents


if __name__ == "__main__":
    documents = load_documents()

    for document in documents:
        print(f"文件名：{document['source']}")
        print(document["content"])
        print("-" * 30)
