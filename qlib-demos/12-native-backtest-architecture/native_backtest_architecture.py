from dataclasses import dataclass, field
from io import StringIO

import pandas as pd


PREDICTIONS = """date,symbol,score,close,next_close
2024-01-10,SH600000,0.010,10.52,10.70
2024-01-10,SZ000001,0.014,12.48,12.70
2024-01-10,SH600519,0.006,1738.00,1760.00
2024-01-11,SH600000,0.007,10.70,10.82
2024-01-11,SZ000001,0.012,12.70,12.82
2024-01-11,SH600519,0.005,1760.00,1772.00
2024-01-12,SH600000,0.009,10.82,10.76
2024-01-12,SZ000001,0.006,12.82,12.78
2024-01-12,SH600519,0.004,1772.00,1765.00
"""


@dataclass
class Order:
    symbol: str
    target_weight: float


class Top1Strategy:
    def generate_orders(self, today_scores: pd.DataFrame) -> list[Order]:
        best = today_scores.sort_values("score", ascending=False).iloc[0]["symbol"]
        return [Order(symbol=best, target_weight=1.0)]


@dataclass
class Account:
    cash: float
    position: dict[str, float] = field(default_factory=dict)

    def total_value(self, prices: dict[str, float]) -> float:
        stock_value = sum(shares * prices.get(symbol, 0.0) for symbol, shares in self.position.items())
        return self.cash + stock_value


class Exchange:
    def __init__(self, cost_rate: float):
        self.cost_rate = cost_rate

    def rebalance_to_single_name(self, account: Account, symbol: str, price: float, current_prices: dict[str, float]) -> float:
        cost = 0.0
        for held_symbol, shares in list(account.position.items()):
            sell_value = shares * current_prices[held_symbol]
            trade_cost = sell_value * self.cost_rate
            account.cash += sell_value - trade_cost
            cost += trade_cost
            account.position.pop(held_symbol)

        target_value = account.cash
        buy_cost = target_value * self.cost_rate
        shares = (target_value - buy_cost) / price
        account.cash = 0.0
        account.position[symbol] = shares
        return cost + buy_cost


class Executor:
    def __init__(self, strategy: Top1Strategy, exchange: Exchange, account: Account):
        self.strategy = strategy
        self.exchange = exchange
        self.account = account

    def run(self, predictions: pd.DataFrame) -> pd.DataFrame:
        reports = []
        for date, group in predictions.groupby("date", sort=True):
            prices = dict(zip(group["symbol"], group["close"]))
            next_prices = dict(zip(group["symbol"], group["next_close"]))
            before = self.account.total_value(prices)
            order = self.strategy.generate_orders(group)[0]
            cost = self.exchange.rebalance_to_single_name(self.account, order.symbol, prices[order.symbol], prices)
            after = self.account.total_value(next_prices)
            reports.append({
                "date": date,
                "selected": order.symbol,
                "value_before": before,
                "trade_cost": cost,
                "value_after_next_close": after,
                "net_return": after / before - 1,
            })
        return pd.DataFrame(reports)


def main() -> None:
    predictions = pd.read_csv(StringIO(PREDICTIONS), parse_dates=["date"])
    executor = Executor(
        strategy=Top1Strategy(),
        exchange=Exchange(cost_rate=0.001),
        account=Account(cash=1_000_000.0),
    )
    report = executor.run(predictions)
    report["equity"] = (1 + report["net_return"]).cumprod()
    print(report.to_string(index=False))


if __name__ == "__main__":
    main()
