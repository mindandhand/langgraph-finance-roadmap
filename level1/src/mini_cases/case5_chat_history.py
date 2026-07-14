"""最小案例 5：保存命令行对话历史

实现一个简单的对话管理器，支持：
- 保存用户和 AI 的消息
- 从 JSON 文件加载历史对话
- 在命令行中显示历史

运行:
    python src/mini_cases/case5_chat_history.py
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
HISTORY_FILE = DATA_DIR / "chat_history.json"


class Message(TypedDict):
    role: str  # "user" | "assistant"
    content: str
    timestamp: str


class ConversationHistory:
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.messages: list[Message] = self._load()

    def _load(self) -> list[Message]:
        if Path(self.filepath).exists():
            try:
                with open(self.filepath, encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return []
        return []

    def add_message(self, role: str, content: str) -> None:
        msg: Message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.messages.append(msg)
        self._save()

    def _save(self) -> None:
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.messages, f, ensure_ascii=False, indent=2)

    def show(self) -> None:
        if not self.messages:
            print("暂无对话历史。")
            return

        print("=" * 60)
        print("对话历史")
        print("=" * 60)
        for msg in self.messages:
            role = "用户" if msg["role"] == "user" else "助手"
            ts = msg["timestamp"][:19].replace("T", " ")
            print(f"\n[{role}] ({ts})")
            print(f"{msg['content']}")

    def clear(self) -> None:
        self.messages.clear()
        self._save()
        print("对话历史已清除。")

    @property
    def count(self) -> int:
        return len(self.messages)


def main() -> None:
    history = ConversationHistory(str(HISTORY_FILE))

    print("对话历史管理器（输入 q 退出，输入 show 查看历史，输入 clear 清除）")
    print("-" * 40)

    while True:
        user_input = input("\n你: ").strip()
        if user_input.lower() == "q":
            break
        if user_input.lower() == "show":
            history.show()
            continue
        if user_input.lower() == "clear":
            history.clear()
            continue

        history.add_message("user", user_input)
        reply = f"已收到你的消息（共 {len(user_input)} 字）。"
        history.add_message("assistant", reply)
        print(f"助手: {reply}")

    print(f"\n本次会话共 {history.count} 条消息。")


if __name__ == "__main__":
    main()
