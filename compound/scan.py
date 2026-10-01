"""Scan + Analyze: find swing setups on the latest bar of each symbol."""
from .indicators import atr, sma
from .models import Bar, Setup

MIN_BARS = 60


def find_setups(symbol: str, bars: list[Bar], reward_risk: float = 2.0) -> list[Setup]:
    if len(bars) < MIN_BARS:
        return []
    closes = [b.close for b in bars]
    last = bars[-1]
    sma20, sma50 = sma(closes, 20), sma(closes, 50)
    a = atr(bars)
    if not a or last.close <= sma50 or sma20 <= sma50:
        return []  # only trade confirmed uptrends

    setups = []
    prior_high = max(b.high for b in bars[-21:-1])
    avg_vol = sum(b.volume for b in bars[-21:-1]) / 20
    if last.close > prior_high and last.volume > 1.5 * avg_vol:
        stop = last.close - 2 * a
        setups.append(Setup(symbol, "breakout", last.day, last.close, stop,
                            last.close + reward_risk * (last.close - stop),
                            f"close {last.close:.2f} > 20d high {prior_high:.2f} on {last.volume / avg_vol:.1f}x volume"))
    elif last.low <= sma20 * 1.01 and last.close > sma20 and last.close > last.open:
        stop = min(last.low, sma20) - a
        setups.append(Setup(symbol, "pullback", last.day, last.close, stop,
                            last.close + reward_risk * (last.close - stop),
                            f"bounced off 20 SMA {sma20:.2f} in uptrend"))
    return setups
