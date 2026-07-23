from __future__ import annotations

from finance_agent import agent


def main() -> None:
    print("Local Finance Agent CLI. Type 'exit' or press Ctrl-C to quit.")

    while True:
        try:
            message = input("\nYou> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not message:
            continue

        if message.lower() in {"exit", "quit", "q"}:
            break

        try:
            response = agent.run(message)
        except Exception as exc:
            print(f"\nAgent error: {exc}")
            continue

        content = getattr(response, "content", response)
        print(f"\nAgent>\n{content}")


if __name__ == "__main__":
    main()
