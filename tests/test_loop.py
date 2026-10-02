import json
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from compound.__main__ import run
from compound.models import Bar, Setup
from compound.risk import RiskConfig, check
from compound.scan import find_setups
from compound.simulate import simulate

D0 = date(2025, 1, 1)


def bar(i, close, high=None, low=None, open_=None, volume=1_000_000):
    return Bar(D0 + timedelta(days=i), open_ if open_ is not None else close,
               high if high is not None else close + 1, low if low is not None else close - 1, close, volume)


def uptrend(n=60, start=50.0, step=0.5):
    return [bar(i, start + i * step) for i in range(n)]


class ScanTest(unittest.TestCase):
    def test_breakout_on_volume(self):
        bars = uptrend()
        bars.append(bar(60, bars[-1].close + 5, volume=3_000_000))
        setups = find_setups("TEST", bars)
        self.assertEqual([s.kind for s in setups], ["breakout"])
        self.assertLess(setups[0].stop, setups[0].entry)

    def test_no_setup_in_downtrend(self):
        bars = uptrend(start=100, step=-0.5)
        bars.append(bar(60, bars[-1].close + 5, volume=3_000_000))
        self.assertEqual(find_setups("TEST", bars), [])

    def test_too_little_history(self):
        self.assertEqual(find_setups("TEST", uptrend(n=30)), [])


class RiskTest(unittest.TestCase):
    def test_sizes_by_risk(self):
        d = check(Setup("T", "breakout", D0, 100, 98, 104), RiskConfig(account_size=10_000))
        self.assertTrue(d.approved)
        self.assertEqual(d.shares, 20)  # capped by 20% max position ($2000 / $100)

    def test_rejects_poor_reward_risk_and_wide_stop(self):
        d = check(Setup("T", "breakout", D0, 100, 80, 110), RiskConfig())
        self.assertFalse(d.approved)
        self.assertEqual(d.shares, 0)
        self.assertEqual(len(d.reasons), 2)

    def test_accepts_exactly_min_reward_risk_despite_rounding(self):
        entry, stop = 87.64, 82.73
        d = check(Setup("T", "pullback", D0, entry, stop, entry + 2 * (entry - stop)), RiskConfig())
        self.assertTrue(d.approved, d.reasons)

    def test_rejects_when_max_positions_reached(self):
        d = check(Setup("T", "breakout", D0, 100, 98, 104), RiskConfig(), open_positions=5)
        self.assertFalse(d.approved)


class SimulateTest(unittest.TestCase):
    setup = Setup("T", "breakout", D0, 100, 95, 110)

    def test_hits_target(self):
        r = simulate(self.setup, 10, [bar(1, 105), bar(2, 109, high=111)])
        self.assertEqual((r.exit_reason, r.exit_price, r.pnl, r.r_multiple), ("target", 110, 100, 2.0))

    def test_stop_checked_first(self):
        r = simulate(self.setup, 10, [bar(1, 100, high=111, low=94)])
        self.assertEqual((r.exit_reason, r.r_multiple), ("stop", -1.0))

    def test_gap_down_fills_at_open(self):
        r = simulate(self.setup, 10, [bar(1, 90, open_=91, low=89)])
        self.assertEqual(r.exit_price, 91)

    def test_time_exit(self):
        r = simulate(self.setup, 10, [bar(i, 101) for i in range(1, 30)], max_days=5)
        self.assertEqual((r.exit_reason, r.exit_day), ("time", D0 + timedelta(days=5)))


class EndToEndTest(unittest.TestCase):
    def test_run_logs_trades(self):
        bars = uptrend()
        bars.append(bar(60, bars[-1].close + 3, volume=3_000_000))
        bars += [bar(61 + i, bars[-1].close + 1 + i) for i in range(20)]
        with tempfile.TemporaryDirectory() as tmp:
            data, journal = Path(tmp, "data"), Path(tmp, "journal.jsonl")
            data.mkdir()
            with open(data / "test.csv", "w") as f:
                f.write("date,open,high,low,close,volume\n")
                for b in bars:
                    f.write(f"{b.day},{b.open},{b.high},{b.low},{b.close},{b.volume}\n")
            trades = run(data, journal, RiskConfig())
            self.assertGreaterEqual(len(trades), 1)
            self.assertEqual(trades[0]["setup"]["symbol"], "TEST")
            events = [json.loads(line)["event"] for line in journal.read_text().splitlines()]
            self.assertIn("paper_trade", events)


if __name__ == "__main__":
    unittest.main()
