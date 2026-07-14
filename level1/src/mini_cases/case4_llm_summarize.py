"""最小案例 4：调用模型总结财报文本

使用 OpenAI API 读取财报文本并让模型生成摘要。
需要先配置 .env 文件中的 OPENAI_API_KEY。

运行:
    python src/mini_cases/case4_llm_summarize.py
"""

from pathlib import Path

from llm_utils import get_client, get_model

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
REPORT_PATH = DATA_DIR / "sample_financial_report.txt"

SUMMARY_SYSTEM_PROMPT = """你是一位专业的金融分析师助手。
请对用户提供的财务报告进行结构化分析，涵盖以下方面：

1. 总体表现评价（营收、利润、现金流）
2. 各业务板块表现
3. 费用结构变化
4. 资产负债状况
5. 主要风险点

请使用简洁的语言，突出关键数据。"""


def read_report(filepath: str) -> str | None:
    try:
        with open(filepath, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"文件不存在: {filepath}")
        return None


def summarize_report(report_text: str) -> str | None:
    client = get_client()
    model = get_model()

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
                {"role": "user", "content": f"请分析以下财务报告：\n\n{report_text}"},
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"API 调用失败: {e}")
        return None


def main() -> None:
    report_text = read_report(str(REPORT_PATH))
    if not report_text:
        return

    print("正在分析财报...")
    summary = summarize_report(report_text)

    if summary:
        print("\n" + "=" * 60)
        print("财报分析结果")
        print("=" * 60)
        print(summary)
    else:
        print("分析失败，请检查 API 配置。")


if __name__ == "__main__":
    main()
