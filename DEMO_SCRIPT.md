# Conviction Agent — Demo Script (2 min)

## What to show, in order

---

### [0:00–0:20] Open the live dashboard
- Go to: https://conviction-agent.onrender.com
- Point out: green pulsing dot (agent is running), portfolio balance, scan count, 13 protocols watched
- **Say:** "This agent runs 24/7 with no human in the loop. It scans 13 crypto protocol GitHub repos and live governance proposals every 30 minutes."

---

### [0:20–0:45] Show the AI reasoning section
- Scroll to the **"QWEN AI ASSESSMENT"** box on the dashboard
- **Say:** "Every scan, Qwen AI reads all the signals and writes a structured market assessment. It's not just a rule engine — it understands context. Here it's explaining *why* Arbitrum's activity is unusual compared to baseline."

---

### [0:45–1:05] Show active signals
- Point to the **Active Signals** cards
- Each card shows: token, conviction score (out of 5), direction (BUY/SELL), position size, and the AI's reason
- **Say:** "When conviction crosses 2 out of 5, the agent executes. Position size scales with confidence — 4% at conviction 2, up to 10% at conviction 5."

---

### [1:05–1:25] Show the trade log
- Scroll to **Trade Log** on the dashboard  
- Or open: https://github.com/Valorian0108/Conviction-Agent/blob/main/paper_trading_log.md
- Show: timestamp, pair, direction, price, quantity, USD amount, balance before/after
- **Say:** "Every trade is logged with full audit trail — timestamp, price, quantity, balance change — pushed to GitHub automatically."

---

### [1:25–1:45] Show the Telegram bot (optional but impressive)
- Open Telegram, find @conviction_agent_demi_bot
- Type `/status` → shows last scan time, signal count, trade count
- Type `/scan` → triggers a manual scan live on screen
- **Say:** "The agent also runs a Telegram bot. You can query it at any time, trigger a manual scan, or check prices."

---

### [1:45–2:00] Show the GitHub repo
- Open: https://github.com/Valorian0108/Conviction-Agent
- Point to the commit history — show the automated "Trade: ARBUSDT BUY" commits
- **Say:** "The repo shows the agent's full history. Every trade creates a commit — real, verifiable, timestamped evidence that this ran autonomously."
- End on the README's architecture diagram

---

## Recording tips
- Record at 1280×720, no browser dev tools visible
- Mute system sounds, use screen recording audio only
- Keep mouse movements slow and deliberate
- Post to Twitter as a public tweet: tag #BitgetHackathon and @BitgetAI
- Submit the tweet link as your demo video URL in the form
