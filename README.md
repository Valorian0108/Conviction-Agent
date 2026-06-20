# Conviction Agent
### Bitget AI Hackathon S1 — Track 1: Trading Agent
**[Live Demo](https://conviction-agent.onrender.com) · [Paper Trading Log](paper_trading_log.md)**

---

## The Problem

Crypto protocol signals are scattered, noisy, and time-sensitive. A spike in Arbitrum commits, an Aave governance proposal gaining quorum, a Chainlink contributor surge — any of these can precede price movement. By the time you manually verify them across GitHub, Snapshot, and forums, the window is gone.

Manual signal aggregation doesn't scale. Traditional quant rules can't interpret context. What's needed is an agent that reads, reasons, and acts — autonomously.

---

## How It Works

Conviction Agent runs a continuous autonomous loop:

### 1 · Perception
- Monitors **13 protocol GitHub repositories** for unusual commit spikes and contributor surges (Arbitrum, Optimism, Chainlink, Uniswap, Aave, Curve, Scroll, Base, Polygon, zkSync, MakerDAO, ENS, Lido)
- Tracks **Snapshot governance proposals** gaining quorum velocity in real time
- Fetches live price data from the Bitget API for signal context

### 2 · Reasoning
- All signals are passed to **Qwen AI** (Alibaba Cloud) which writes a structured, natural-language market assessment
- Qwen weighs signal strength, recent momentum, and cross-protocol correlation
- Falls back to a deterministic conviction scorer when AI is unavailable

### 3 · Decision & Execution
- A conviction score (1–5) is assigned per token based on the AI's assessment
- Trades are only executed when conviction ≥ 2 (configurable threshold)
- Position size scales linearly with conviction: 2% (weak) → 10% (strong)
- Executed via Bitget simulated trading — no real capital required

### 4 · Risk Management & Monitoring
- **30-minute per-token cooldown** prevents duplicate trades in a single scan cycle
- **Full audit trail** pushed to GitHub after every trade (timestamp, pair, direction, price, quantity, balance)
- Flask dashboard at [conviction-agent.onrender.com](https://conviction-agent.onrender.com) shows live signals, portfolio state, and scan history
- Telegram bot delivers real-time alerts (deduped — only fires when new signals appear)

---

## What Makes It Different

| Capability | Conviction Agent | Rules-based bot | LLM chatbot |
|------------|-----------------|-----------------|-------------|
| Reads GitHub dev activity | ✅ | ❌ | ❌ |
| Reads governance proposals | ✅ | ❌ | ❌ |
| Natural language reasoning | ✅ (Qwen) | ❌ | ✅ |
| Autonomous execution loop | ✅ | ✅ | ❌ |
| Live audit trail | ✅ | sometimes | ❌ |

Most trading bots react to price. Conviction Agent acts on **developer intent** — the signal that precedes price.

---

## Evidence

**Paper trading log:** [`paper_trading_log.md`](paper_trading_log.md)  
All columns required by the hackathon are present: timestamp, trading pair, direction, price, quantity, USD amount, balance before, balance after, conviction score.

**Live demo:** [conviction-agent.onrender.com](https://conviction-agent.onrender.com)  
Dashboard shows: active signals, AI reasoning summary, last scan time, portfolio value, and full trade history.

**Scan cycle:** every 30 minutes, autonomous, no human input.

---

## Architecture

```
github_watcher.py     → monitors 13 protocol repos (GitHub API, authenticated)
governance_watcher.py → monitors Snapshot governance proposals (GraphQL)
ai_reasoning.py       → Qwen AI signal interpreter (Alibaba Cloud)
conviction.py         → fallback scoring engine + TOKEN_MAP
executor.py           → sim trade execution + balance tracking + cooldown
notifier.py           → Telegram alert dispatch (deduped)
github_logger.py      → pushes trade records to paper_trading_log.md
app.py                → Flask dashboard + background scan loop
bot.py                → Telegram command interface (/status, /scan, /portfolio)
```

---

## Stack

- **Language:** Python 3, Flask
- **AI:** Qwen (Alibaba Cloud) — hackathon strategic partner
- **Data:** GitHub REST API (authenticated, 5000 req/hr), Snapshot GraphQL API
- **Exchange:** Bitget REST API (price data + sim execution)
- **Alerts:** Telegram Bot API
- **Hosting:** Render (web service, continuous deployment from GitHub)

---

## Run Locally

```bash
pip install flask requests python-dotenv
cp .env.example .env   # fill in your keys
python app.py
```

**Required env vars:**
```
QWEN_API_KEY=
BITGET_API_KEY=
BITGET_API_SECRET=
BITGET_PASSPHRASE=
GITHUB_TOKEN=
TELEGRAM_TOKEN=
TELEGRAM_CHAT_ID=
```

---

## Submission

**Track:** 🟦 Track 1 · Trading Agent  
**Hackathon:** Bitget AI Base Camp Hackathon S1 (May 27 – June 30, 2026)
