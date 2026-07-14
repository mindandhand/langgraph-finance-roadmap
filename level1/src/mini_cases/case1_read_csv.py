"""最小案例 1：读取股票历史 CSV 数据

使用 Pandas 读取 CSV 文件，查看数据结构和基本统计信息。

运行:
    python src/mini_cases/case1_read_csv.py
"""

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
CSV_PATH = DATA_DIR / "sample_stock_data.csv"


def load_stock_data(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath, parse_dates=["date"])
    df = df.sort_values("date").reset_index(drop=True)
    return df


def main() -> None:
    if not CSV_PATH.exists():
        print(f"数据文件不存在: {CSV_PATH}")
        print("请先检查 data/ 目录下是否有 CSV 文件。")
        return

    df = load_stock_data(str(CSV_PATH))

    print("=" * 50)
    print("股票数据概览")
    print("=" * 50)
    print(f"数据范围: {df['date'].min().date()} 至 {df['date'].max().date()}")
    print(f"交易日数: {len(df)}")
    print(f"列名: {list(df.columns)}")
    print()

    print("前 5 行数据:")
    print(df.head().to_string(index=False))
    print()

    print("基本统计信息:")
    print(df[["open", "high", "low", "close", "volume"]].describe().round(2))
    print()

    print("数据类型:")
    print(df.dtypes)


if __name__ == "__main__":
    main()
