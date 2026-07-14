"""最小案例 3：计算 20 日移动平均线

计算收盘价的 20 日简单移动平均线 (SMA)，并与收盘价对比。

运行:
    python src/mini_cases/case3_moving_average.py
"""

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
CSV_PATH = DATA_DIR / "sample_stock_data.csv"

WINDOW = 20


def load_stock_data(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath, parse_dates=["date"])
    df = df.sort_values("date").reset_index(drop=True)
    return df


def add_moving_average(df: pd.DataFrame, window: int = WINDOW) -> pd.DataFrame:
    """添加 N 日移动平均线。"""
    result = df[["date", "close"]].copy()
    result["ma"] = result["close"].rolling(window=window).mean()
    return result


def main() -> None:
    if not CSV_PATH.exists():
        print(f"数据文件不存在: {CSV_PATH}")
        return

    df = load_stock_data(str(CSV_PATH))
    ma_df = add_moving_average(df)

    print("=" * 60)
    print(f"{WINDOW} 日移动平均线分析")
    print("=" * 60)
    print(f"{'日期':<14} {'收盘价':>10} {'移动平均':>10} {'偏离度':>10}")
    print("-" * 46)
    for _, row in ma_df.iterrows():
        deviation = (row["close"] / row["ma"] - 1) if pd.notna(row["ma"]) else 0
        close_str = f"{row['close']:.2f}"
        ma_str = f"{row['ma']:.2f}" if pd.notna(row["ma"]) else "N/A"
        dev_str = f"{deviation:.4%}" if pd.notna(row["ma"]) else "N/A"
        print(f"{row['date'].strftime('%Y-%m-%d'):<14} {close_str:>10} {ma_str:>10} {dev_str:>10}")

    print()
    last = ma_df.dropna().iloc[-1]
    print(f"最新收盘价: {last['close']:.2f}")
    print(f"最新 {WINDOW} 日移动平均: {last['ma']:.2f}")
    print(f"当前价格偏离均线: {(last['close'] / last['ma'] - 1):.4%}")


if __name__ == "__main__":
    main()
