from llm_service import generate_answer

result = generate_answer(
    system_prompt="你是一个 Python 助手。",
    user_prompt="请解释 Python 中 list.append() 的作用。"
)

print(result)