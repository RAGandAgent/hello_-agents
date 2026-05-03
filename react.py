from LLM import HelloAgentsLLM
from registerTool import ToolExecutor
import re

REACT_PROMPT_TEMPLATE = """
请注意，你是一个有能力调用外部工具的智能助手。

可用工具如下：
{tools}

请严格按照以下格式进行回应：

Thought: 你的思考过程，用于分析问题、拆解任务和规划下一步行动。

Action: 你决定采取的行动，必须是以下格式之一：
- `{{tool_name}}[{{tool_input}}]`：调用一个可用工具。
- `Finish[最终答案]`：当你认为已经获得最终答案时。
- 当你收集到足够的信息，能够回答用户的最终问题时，你必须在Action:字段后使用 Finish[最终答案] 来输出最终答案。

现在，请开始解决以下问题：
Question: {question}
History: {history}
"""


class RrActAgent:
    def __init__(self, LLM: HelloAgentsLLM, tool_executor: ToolExecutor, max_steps: int = 5) -> None:
        self.LLM = LLM
        self.tool_executor = tool_executor
        self.max_steps = max_steps
        self.history = []

    def run(self, question: str):
        """
        运行智能体来回答一个问题
        """
        self.history = []  # 重置历史记录
        current_step = 0

        while current_step < self.max_steps:
            current_step += 1
            print(f"第 {current_step} 步")

            # 格式化提示词
            tools_description = self.tool_executor.getAvailableTools()
            history_str = "\n".join(self.history)
            prompt = REACT_PROMPT_TEMPLATE.format(
                history=history_str,
                question=question,
                tools=tools_description
            )

            # 调用LLM生成回复
            messages = [{"role": "user", "content": prompt}]
            response = self.LLM.think(messages=messages)
            if not response:
                print("智能体回复为空，无法继续。")
                break
            thought, action = self._parse_output(response)
            if thought:
                print(f"Thought: {thought}")
            if not action:
                print("Action 为空，无法继续。")
                break

            if action.startswith("Finish"):
                final_answer = re.match(r"Finish\[(.*)\]", action).group(1)
                print(f"Final Answer: {final_answer}")
                return final_answer
            
            tool_name, tool_input = self._parse_action(action)
            if not tool_name or not tool_input:
                continue
            
            print(f"Action: {tool_name} [{tool_input}]")
            tool_function = self.tool_executor.getTool(tool_name)
            if not tool_function:
                observation = print(f"工具 {tool_name} 不存在。")
            else:
                observation = tool_function(tool_input)
                print(f"工具 {tool_name} 输出: {observation}")

                self.history.append(f"Action {tool_name} [{tool_input}]")
                self.history.append(f"Observation: {observation}")
        self.history.append(f"action: {action}")
        self.history.append(f"observation: {observation}")
        return None


    def _parse_output(self, output: str):
        """解析LLM的输出，提取Thought和Action。"""
        thought_matach = re.search(r"Thought:\s*(.+)", output, re.DOTALL)

        action_matach = re.search(r"Action:\s*(.+)", output, re.DOTALL)
        thought = thought_matach.group(1).strip() if thought_matach else ""
        action = action_matach.group(1).strip() if action_matach else ""
        return thought, action
    
    def _execute_action(self, action: str):
        """解析Action字符串，提取工具名称和输入。"""
        match = re.match(r"(\w+)\[(.*)\]", action, re.DOTALL)
        if match:
            return match.group(1), match.group(2)
        return None, None

    
    
