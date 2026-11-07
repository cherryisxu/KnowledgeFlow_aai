
import re


def chunk_text(
    text: str,
    chunk_size: int = 300,
    overlap: int = 50,
) -> list[str]:
    """
    按 Markdown 标题和段落切分文本。
    保留标题层级作为 Chunk 的上下文。
    忽略代码块中的 Markdown 标题符号。
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size 必须大于 0")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap 必须大于等于 0 且小于 chunk_size")

    text = text.strip()

    if not text:
        return []

    heading_stack = []
    sections = []
    current_lines = []

    in_code_block = False

    # 第一阶段：识别 Markdown 标题，维护标题层级
    for line in text.splitlines():

        stripped_line = line.strip()

        # 识别代码块开始和结束
        if stripped_line.startswith("```") or stripped_line.startswith("~~~"):
            in_code_block = not in_code_block
            current_lines.append(line)
            continue

        # 代码块内部不识别标题
        if in_code_block:
            current_lines.append(line)
            continue

        # 兼容普通标题和加粗标题
        match = re.match(
            r"^\s*(?:\*\*)?(#{1,6})\s+(.+?)\s*(?:\*\*)?\s*$",
            line,
        )

        if match:
            # 只有当前 section 包含正文时才保存
            previous_content = [
                item for item in current_lines
                if item.strip() and not re.match(r"^\s*#{1,6}\s+", item)
            ]

            if previous_content:
                sections.append("\n".join(current_lines).strip())

            level = len(match.group(1))
            title = f"{match.group(1)} {match.group(2).strip()}"

            # 删除同级和更深层级标题
            heading_stack = [
                item for item in heading_stack
                if item[0] < level
            ]

            heading_stack.append((level, title))

            # 当前 section 继承完整标题路径
            current_lines = [
                item[1] for item in heading_stack
            ]

        else:
            current_lines.append(line)

    # 保存最后一个 section
    previous_content = [
        item for item in current_lines
        if item.strip() and not re.match(r"^\s*#{1,6}\s+", item)
    ]

    if previous_content:
        sections.append("\n".join(current_lines).strip())

    # 第二阶段：按照段落和长度切分
    chunks = []

    for section in sections:
        lines = section.splitlines()

        headings = [
            line for line in lines
            if re.match(r"^\s*#{1,6}\s+", line)
        ]

        body = [
            line for line in lines
            if not re.match(r"^\s*#{1,6}\s+", line)
        ]

        body_text = "\n".join(body).strip()

        if not body_text:
            continue

        paragraphs = re.split(r"\n\s*\n", body_text)

        current_chunk = ""

        for paragraph in paragraphs:
            paragraph = paragraph.strip()

            if not paragraph:
                continue

            # 超长段落单独切分
            if len(paragraph) > chunk_size:
                if current_chunk:
                    chunks.append(
                        "\n".join(headings + [current_chunk])
                    )
                    current_chunk = ""

                step = chunk_size - overlap

                for start in range(0, len(paragraph), step):
                    part = paragraph[start:start + chunk_size]

                    chunks.append(
                        "\n".join(headings + [part])
                    )

                    if start + chunk_size >= len(paragraph):
                        break

                continue

            candidate = (
                f"{current_chunk}\n\n{paragraph}"
                if current_chunk
                else paragraph
            )

            if len(candidate) <= chunk_size:
                current_chunk = candidate
            else:
                if current_chunk:
                    chunks.append(
                        "\n".join(headings + [current_chunk])
                    )

                current_chunk = paragraph

        if current_chunk:
            chunks.append(
                "\n".join(headings + [current_chunk])
            )

    return chunks
