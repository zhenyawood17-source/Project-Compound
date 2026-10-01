"""Run the loop over historical CSVs in paper mode.

    python -m compound DATA_DIR [--log logs/journal.jsonl] [--account 10000]

Walks every day in the data, scans for setups using only bars up to that day,
risk-checks them, paper-trades approved ones on the bars that follow, and logs everything.
"""
import argparse
from pathlib import Path

from .data import load_dir
from .journal import log
from .risk import RiskConfig, check
from .scan import MIN_BARS, find_setups
from .simulate import simulate


def run(data_dir: Path, log_path: Path, cfg: RiskConfig) -> list[dict]:
    trades = []
    for symbol, bars in load_dir(data_dir).items():
        busy_until = None
        for i in range(MIN_BARS, len(bars)):
            if busy_until and bars[i - 1].day <= busy_until:
                continue  # one position per symbol at a time
            for setup in find_setups(symbol, bars[:i]):
                decision = check(setup, cfg)
                log(log_path, "risk_check", setup=setup, decision=decision)
                if not decision.approved:
                    continue
                result = simulate(setup, decision.shares, bars[i:])
                trades.append(log(log_path, "paper_trade", setup=setup, shares=decision.shares, result=result))
                busy_until = result.exit_day
    return trades


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("data_dir", type=Path)
    p.add_argument("--log", type=Path, default=Path("logs/journal.jsonl"))
    p.add_argument("--account", type=float, default=10_000.0)
    args = p.parse_args()

    trades = run(args.data_dir, args.log, RiskConfig(account_size=args.account))
    closed = [t for t in trades if t["result"]["exit_reason"] != "open"]
    wins = [t for t in closed if t["result"]["pnl"] > 0]
    total = sum(t["result"]["pnl"] for t in closed)
    avg_r = sum(t["result"]["r_multiple"] for t in closed) / len(closed) if closed else 0.0
    print(f"paper trades: {len(trades)} ({len(closed)} closed)")
    if closed:
        print(f"win rate: {len(wins) / len(closed):.0%}  avg R: {avg_r:+.2f}  total P&L: ${total:,.2f}")
    print(f"journal: {args.log}")


if __name__ == "__main__":
    main()
