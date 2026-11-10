import os
import json

from openai import OpenAI
from dotenv import load_dotenv

from agent.schemas import LLMResponse, LLMToolCall


load_dotenv()


class LLMService:
    """统一的大模型调用服务"""

    def __init__(self):
        api_key = os.getenv("DEEPSEEK_API_KEY")
        base_url = os.getenv("DEEPSEEK_BASE_URL")
        self.model = os.getenv("DEEPSEEK_MODEL")

        if not api_key:
            raise RuntimeError("DEEPSEEK_API_KEY 未配置")

        if not self.model:
            raise RuntimeError("DEEPSEEK_MODEL 未配置")

        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )

    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        temperature: float = 0.2
    ) -> LLMResponse:
        """统一模型调用接口"""

        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature
        }

        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        response = self.client.chat.completions.create(**kwargs)

        message = response.choices[0].message

        tool_calls = []

        if message.tool_calls:
            for call in message.tool_calls:
                arguments = json.loads(call.function.arguments)

                tool_calls.append(
                    LLMToolCall(
                        id=call.id,
                        name=call.function.name,
                        arguments=arguments
                    )
                )

        return LLMResponse(
            content=message.content,
            tool_calls=tool_calls,
            finish_reason=response.choices[0].finish_reason
        )


# 创建统一服务实例
llm_service = LLMService()


# 保留旧接口，避免影响现有 RAG 功能
def generate_answer(system_prompt: str, user_prompt: str):
    response = llm_service.chat(
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )

    return response.content