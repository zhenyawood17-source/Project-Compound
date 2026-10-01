# Project-Compound
Project Compound is an AI-assisted swing-trading system that scans markets, analyzes setups, applies strict risk controls, logs every decision, and learns from results over time. Built around a Scan → Analyze → Risk Check → Simulate → Log → Review → Learn loop, with human approval required for real trades.

## Robinhood Trading MCP

The repo registers Robinhood's trading MCP server in `.mcp.json` (project scope), so Claude Code picks it up automatically when opened in this directory:

```json
{
  "mcpServers": {
    "robinhood-trading": {
      "type": "http",
      "url": "https://agent.robinhood.com/mcp/trading"
    }
  }
}
```

Setup:

1. Start Claude Code in the repo and approve the project MCP server when prompted.
2. Run `/mcp`, select `robinhood-trading`, and complete the Robinhood sign-in (OAuth) in your browser.

No Robinhood tools are pre-approved in `.claude/settings.json`. Claude Code asks for permission on every call, which is the human-approval gate for real trades. Don't add these tools to an allowlist.

## Paper-trading loop

Python 3.10+ with no dependencies. Paper mode only: nothing here places real orders.

```
python -m compound path/to/data_dir        # one SYMBOL.csv per stock: date,open,high,low,close,volume
python -m unittest discover -s tests       # run tests
```

| Step | Module | What it does |
|---|---|---|
| Scan + Analyze | `compound/scan.py` | Uptrend filter (close > 50 SMA, 20 SMA > 50 SMA), then **breakout** (close above 20-day high on 1.5x volume) or **pullback** (bounce off the 20 SMA). Stops are ATR-based, targets 2R. |
| Risk Check | `compound/risk.py` | Risk 1% of account per trade, cap one position at 20% of account, require reward/risk ≥ 2, reject stops > 10% away, cap at 5 open positions. |
| Simulate | `compound/simulate.py` | Paper-trades forward: stop (checked first, gaps fill at the open), target, or 20-day time exit. |
| Log | `compound/journal.py` | Appends every risk check and paper trade to `logs/journal.jsonl`. |

Review and Learn come next.
