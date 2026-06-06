# Conviction Agent
### Bitget AI Hackathon S1. Track 1: Trading Agent

An autonomous AI trading agent that solves a real problem for crypto creators:
by the time you manually verify scattered signals, the market has already moved.

## The Problem
Signals are scattered across GitHub, governance forums, and on-chain data.
Manual verification takes hours. The opportunity is gone before you act.

## How It Works

**PERCEPTION**
- Monitors 7 protocol GitHub repos for unusual commit spikes and contributor surges
- Tracks Snapshot governance proposals gaining quorum velocity

**DECISION**
- Qwen AI (Alibaba Cloud) reads all signals and writes a reasoned market assessment
- Decides whether conditions justify a trade and at what conviction level

**EXECUTION**
- When conviction threshold is crossed, executes position via Bitget spot API
- Position size scales with conviction (2-10% of portfolio)

**RISK MANAGEMENT**
- Sim mode by default - no real capital required
- Full trade log with timestamps and prices as evidence

## Stack
- Python, Flask, Requests
- GitHub REST API (dev activity monitoring)
- Snapshot GraphQL API (governance tracking)
- Qwen AI via Alibaba Cloud (reasoning engine)
- Bitget REST API (price data + execution)

## Files
- github_watcher.py - monitors protocol dev activity
- governance_watcher.py - tracks governance proposals
- ai_reasoning.py - Qwen AI signal interpretation
- conviction.py - fallback scoring engine
- executor.py - sim trade execution
- app.py - Flask dashboard

## Live Demo
https://ae4fd2f2-8e36-4802-94f7-79777b91b732-00-uy0ygun8lsnl.kirk.replit.dev:5000

## Run Locally
pip install flask requests python-dotenv
export QWEN_API_KEY=your-key
export BITGET_API_KEY=your-key
python app.py
