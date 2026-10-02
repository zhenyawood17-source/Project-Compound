"""Risk Check: hard rules every setup must pass before it can be simulated."""
from dataclasses import dataclass

from .models import RiskDecision, Setup


@dataclass
class RiskConfig:
    account_size: float = 10_000.0
    risk_per_trade: float = 0.01      # max fraction of account lost if stopped out
    max_position_pct: float = 0.20    # max fraction of account in one position
    max_open_positions: int = 5
    min_reward_risk: float = 2.0
    max_stop_pct: float = 0.10        # reject stops wider than 10% of entry


def check(setup: Setup, cfg: RiskConfig, open_positions: int = 0) -> RiskDecision:
    reasons = []
    if setup.risk_per_share <= 0:
        return RiskDecision(False, 0, ["stop is not below entry"])
    if open_positions >= cfg.max_open_positions:
        reasons.append(f"already {open_positions} open positions (max {cfg.max_open_positions})")
    if setup.reward_risk < cfg.min_reward_risk - 1e-9:  # tolerate float rounding at exactly the minimum
        reasons.append(f"reward/risk {setup.reward_risk:.2f} < {cfg.min_reward_risk}")
    if setup.risk_per_share / setup.entry > cfg.max_stop_pct:
        reasons.append(f"stop {setup.risk_per_share / setup.entry:.1%} away exceeds {cfg.max_stop_pct:.0%}")

    shares = int(min(cfg.account_size * cfg.risk_per_trade / setup.risk_per_share,
                     cfg.account_size * cfg.max_position_pct / setup.entry))
    if shares < 1:
        reasons.append("position size rounds to 0 shares")
    return RiskDecision(not reasons, shares if not reasons else 0, reasons)
