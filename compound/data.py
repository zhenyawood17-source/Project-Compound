import csv
from datetime import date
from pathlib import Path

from .models import Bar


def load_csv(path: Path) -> list[Bar]:
    """Load daily bars from a CSV with columns date,open,high,low,close,volume."""
    bars = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            row = {k.strip().lower(): v for k, v in row.items()}
            bars.append(Bar(
                day=date.fromisoformat(row["date"]),
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
                volume=float(row["volume"]),
            ))
    bars.sort(key=lambda b: b.day)
    return bars


def load_dir(directory: Path) -> dict[str, list[Bar]]:
    """Load every SYMBOL.csv in a directory."""
    return {p.stem.upper(): load_csv(p) for p in sorted(Path(directory).glob("*.csv"))}
