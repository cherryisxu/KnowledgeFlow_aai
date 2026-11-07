
from pathlib import Path
from text_splitter import chunk_text

# 1. 读取真实的 Markdown 文档
file_path = Path("documents/python_uselist.md")
original_text = file_path.read_text(encoding="utf-8")

# 2. 使用当前切分器进行切分
chunks = chunk_text(original_text)

# 3. 合并所有 Chunk，检查原文中的关键命令是否完整保留
all_content = "\n".join(chunks)

print("\n===== 代码围栏配对检查 =====")

for i, chunk in enumerate(chunks, start=1):
    fence_lines = [
        line.strip()
        for line in chunk.splitlines()
        if line.strip().startswith("```")
        or line.strip().startswith("~~~")
    ]

    print(f"Chunk {i}: {len(fence_lines)} 行代码围栏")

    if len(fence_lines) % 2 != 0:
        print("  ⚠️ 围栏数量为奇数，请检查这个 Chunk")

expected_commands = [
    "pip install matplotlib==3.7.0",
    "pip install --upgrade matplotlib",
    "pip uninstall matplotlib",
    "pip list",
    "pip install matplotlib -i https://pypi.tuna.tsinghua.edu.cn/simple",
]

print(f"原文字符数：{len(original_text)}")
print(f"生成 Chunk 数量：{len(chunks)}")
print(f"所有 Chunk 的字符总数：{sum(len(c) for c in chunks)}")

print("\n===== 关键命令完整性检查 =====")

all_passed = True

for command in expected_commands:
    passed = command in all_content
    print(f"[{'通过' if passed else '失败'}] {command}")

    if not passed:
        all_passed = False

# 4. 检查代码围栏数量，辅助发现代码块边界异常
fence_count = sum(
    1
    for chunk in chunks
    for line in chunk.splitlines()
    if line.strip().startswith("```") or line.strip().startswith("~~~")
)

print(f"\nChunk 中代码围栏行数（含重复标题等内容）：{fence_count}")

if all_passed:
    print("\n初步检查通过：所有指定命令都能在 Chunk 中找到。")
else:
    print("\n检查未通过：请核对原文和切分结果。")
