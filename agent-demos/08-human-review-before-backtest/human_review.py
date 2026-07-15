def request_review(payload: dict) -> bool:
    print("Pending backtest request:")
    for key, value in payload.items():
        print(f"  {key}: {value}")
    answer = input("Approve backtest? (yes/no): ").strip().lower()
    return answer in {"y", "yes"}


if __name__ == "__main__":
    approved = request_review({
        "factor": "momentum_3d",
        "period": "2024-01-01 to 2024-03-31",
        "max_backtests_used": "0 / 1",
    })
    print("decision:", "approved" if approved else "rejected")
