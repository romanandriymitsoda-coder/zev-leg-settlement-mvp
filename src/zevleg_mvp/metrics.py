from __future__ import annotations

def deltas(alloc: dict[str, float], outside: dict[str, float]) -> dict[str, float]:
    return {k: alloc[k] - outside[k] for k in alloc}

def loser_share(delta: dict[str, float]) -> float:
    losers = sum(1 for v in delta.values() if v > 0)
    return losers / len(delta)

def max_increase(delta: dict[str, float]) -> float:
    return max(0.0, max(delta.values()))
