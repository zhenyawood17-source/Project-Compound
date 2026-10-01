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
