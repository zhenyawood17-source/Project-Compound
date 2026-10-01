"""Simulate: paper-trade a setup forward over later bars. Never places real orders."""
from .models import Bar, Setup, TradeResult


def simulate(setup: Setup, shares: int, future: list[Bar], max_days: int = 20) -> TradeResult:
    """Stop is checked before target on the same bar (conservative)."""
    for i, bar in enumerate(future[:max_days]):
        if bar.low <= setup.stop:
            price, reason = min(bar.open, setup.stop), "stop"  # gap-down fills at open
        elif bar.high >= setup.target:
            price, reason = max(bar.open, setup.target), "target"
        elif i == max_days - 1:
            price, reason = bar.close, "time"
        else:
            continue
        return _result(setup, shares, bar, price, reason)
    if not future:
        return TradeResult(setup.day, setup.entry, "open", 0.0, 0.0)
    return _result(setup, shares, future[min(len(future), max_days) - 1],
                   future[min(len(future), max_days) - 1].close, "open")


def _result(setup: Setup, shares: int, bar: Bar, price: float, reason: str) -> TradeResult:
    return TradeResult(bar.day, price, reason, (price - setup.entry) * shares,
                       (price - setup.entry) / setup.risk_per_share)
