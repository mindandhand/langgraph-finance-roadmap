"""最小案例 2：计算每日收益率

基于收盘价计算每日收益率和累计收益率。

运行:
    python src/mini_cases/case2_daily_return.py
"""

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
CSV_PATH = DATA_DIR / "sample_stock_data.csv"


def load_stock_data(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath, parse_dates=["date"])
    df = df.sort_values("date").reset_index(drop=True)
    return df


def calculate_returns(df: pd.DataFrame) -> pd.DataFrame:
    """计算每日收益率和累计收益率。"""
    result = df[["date", "close"]].copy()

    # 每日收益率 = (当日收盘价 - 前日收盘价) / 前日收盘价
    result["daily_return"] = result["close"].pct_change()

    # 累计收益率 = (1 + 每日收益率) 累乘 - 1
    result["cumulative_return"] = (1 + result["daily_return"]).cumprod() - 1

    return result


def main() -> None:
    if not CSV_PATH.exists():
        print(f"数据文件不存在: {CSV_PATH}")
        return

    df = load_stock_data(str(CSV_PATH))
    returns_df = calculate_returns(df)

    print("=" * 60)
    print("每日收益率分析")
    print("=" * 60)
    print(returns_df.to_string(index=False, float_format=lambda x: f"{x:.6f}" if pd.notna(x) else "NaN"))
    print()

    print(f"期间累计收益率: {returns_df['cumulative_return'].iloc[-1]:.2%}")
    print(f"平均每日收益率: {returns_df['daily_return'].mean():.6f}")
    print(f"每日收益率标准差: {returns_df['daily_return'].std():.6f}")
    print(f"最高单日收益率: {returns_df['daily_return'].max():.4%}")
    print(f"最低单日收益率: {returns_df['daily_return'].min():.4%}")


if __name__ == "__main__":
    main()
