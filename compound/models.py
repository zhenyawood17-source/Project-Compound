from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class Bar:
    day: date
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class Setup:
    symbol: str
    kind: str  # "breakout" or "pullback"
    day: date
    entry: float
    stop: float
    target: float
    notes: str = ""

    @property
    def risk_per_share(self) -> float:
        return self.entry - self.stop

    @property
    def reward_risk(self) -> float:
        return (self.target - self.entry) / self.risk_per_share


@dataclass
class RiskDecision:
    approved: bool
    shares: int
    reasons: list[str] = field(default_factory=list)


@dataclass
class TradeResult:
    exit_day: date
    exit_price: float
    exit_reason: str  # "stop", "target", "time", "open"
    pnl: float
    r_multiple: float
