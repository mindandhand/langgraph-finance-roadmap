NOTES = [
    {"id": "note-001", "text": "Short-term momentum can be unstable after costs because turnover is high."},
    {"id": "note-002", "text": "Rank IC is preferred when factor scale is unstable but ordering may still help."},
    {"id": "note-003", "text": "Do not use final holdout repeatedly when tuning factor windows."},
]


def retrieve(query: str, k: int = 2) -> list[dict]:
    words = {w.lower().strip(".,") for w in query.split()}
    scored = []
    for note in NOTES:
        score = sum(1 for word in words if word in note["text"].lower())
        scored.append((score, note))
    return [note for score, note in sorted(scored, key=lambda x: x[0], reverse=True)[:k] if score > 0]


if __name__ == "__main__":
    query = "Should I trust a short-term momentum factor with high turnover?"
    hits = retrieve(query)
    print("query:", query)
    for hit in hits:
        print(f"{hit['id']}: {hit['text']}")
