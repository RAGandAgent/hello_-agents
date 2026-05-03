import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict


load_dotenv()


class HelloAgentsLLM:
    def __init__(
        self,
        model: str = None,
        api_key: str = None,
        base_url: str = None,
        timeout: int = None,
    ):
        self.model = model or os.getenv("OPENAI_MODEL")
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        base_url = base_url or os.getenv("OPENAI_BASE_URL")
        timeout = timeout or int(os.getenv("TIMEOUT", 60))

        if not all([self.model, api_key, base_url]):
            raise ValueError("模型、API密钥和基础URL必须在.env文件中提供")
        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)

    def think(self, messages: List[Dict[str, str]], temperature: float = 1) -> str:
        """
        生成模型的思考结果
        """
        print(f"正在调用{self.model}模型...")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=True,
            )
            print("大语言模型响应成功:")
            collected_content = []
            for chunk in response:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        content = delta.content
                        print(content, end="", flush=True)
                        collected_content.append(content)
            print()
            return "".join(collected_content)

        except Exception as e:
            print(f"调用LLM API时发生错误: {e}")
            return None


if __name__ == "__main__":
    try:
        llm = HelloAgentsLLM()

        exampleMessages = [
            {"role": "system","content": "You are a helpful assistant that writes Python code.",},
            {"role": "user", "content": "写一个快速排序算法"},
        ]

        print("---调用LLM模型---")
        response = llm.think(exampleMessages)
        if response:
            print("模型正常响应:")
            print(response)
        else:
            print("模型响应为空")

    except Exception as e:
        print(f"发生错误: {e}")
