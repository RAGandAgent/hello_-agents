from typing import List, Dict, Any, Optional

class Memoty:
    """
    一个简单的记忆模块，用于存储智能体的行动与反思轨迹
    """
    def __init__(self) -> None:
        self.records: List[Dict[str, Any]] = []

    def add(self, record_type: str, content: str) -> None:
        """
        添加一条记忆
        :param record_type: 记录类型， ('execution' 或 'reflection')。
        :param content: 记录的具体内容 (例如，生成的代码或反思的反馈)。
        """
        record = {"record_type": record_type, "content": content}
        self.records.append(record)
        print(f"记忆已更新，记录类型：{record_type}，记录内容：{content}")
    
    def get_records(self):
        """
        将所有记忆记录格式化为一个连贯的字符串文本，用于构建提示词。
        """
        trajectory_parts = []
        for record in self.records:
            if record["record_type"] == "execution":
                trajectory_parts.append(f"执行：{record['content']}")
            elif record["record_type"] == "reflection":
                trajectory_parts.append(f"反思：{record['content']}")
        return "\n".join(trajectory_parts)

    def get_last_execution(self) -> Optional[str]:
        """
        获取最近一次的执行结果 (例如，最新生成的代码)。
        如果不存在，则返回 None。
        """
        for record in reversed(self.records):
            if record["record_type"] == "execution":
                return record["content"]
        return None

       

