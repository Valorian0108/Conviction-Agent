import requests, os, base64, json

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
REPO = 'Valorian0108/Conviction-Agent'
API = 'https://api.github.com'

def _headers():
    return {'Authorization': 'token ' + GITHUB_TOKEN, 'Content-Type': 'application/json'}

def _get_file(path):
    if not GITHUB_TOKEN:
        return None, None
    try:
        r = requests.get(f'{API}/repos/{REPO}/contents/{path}', headers=_headers(), timeout=10)
        if r.status_code == 200:
            d = r.json()
            return base64.b64decode(d['content']).decode('utf-8'), d['sha']
    except: pass
    return None, None

def _put_file(path, content_str, sha, message):
    if not GITHUB_TOKEN:
        return False
    try:
        payload = {'message': message, 'content': base64.b64encode(content_str.encode()).decode()}
        if sha:
            payload['sha'] = sha
        r = requests.put(f'{API}/repos/{REPO}/contents/{path}', headers=_headers(), json=payload, timeout=15)
        return r.status_code in [200, 201]
    except Exception as e:
        print('GitHub put failed: ' + str(e))
        return False

def push_trade(trade):
    if not GITHUB_TOKEN:
        print('No GITHUB_TOKEN - skipping push')
        return
    try:
        # Only update paper_trading_log.md (required for hackathon evidence)
        # trade_log.json is NOT pushed to GitHub - it was triggering a rebuild on
        # every trade via Render auto-deploy, burning through free pipeline minutes
        current, sha = _get_file('paper_trading_log.md')
        row = (
            '| ' + str(trade.get('timestamp', ''))[:19].replace('T', ' ') +
            ' | ' + str(trade.get('token', '')) +
            ' | ' + str(trade.get('action', '')) +
            ' | $' + str(trade.get('price', '')) +
            ' | ' + str(trade.get('quantity', '')) +
            ' | $' + str(trade.get('usd_amount', '')) +
            ' | $' + str(trade.get('balance_before', '')) +
            ' | $' + str(trade.get('balance_after', '')) +
            ' | ' + str(trade.get('conviction', '')) + '/5 |'
        )
        TABLE_HEADER = (
            '# Paper Trading Log — Conviction Agent\n\n'
            '| Timestamp | Pair | Direction | Price | Quantity | USD Amount | Balance Before | Balance After | Conviction |\n'
            '|-----------|------|-----------|-------|----------|------------|----------------|---------------|------------|'
        )
        if current and current.strip():
            body = current.strip()
            if not body.startswith('#'):
                body = TABLE_HEADER + '\n' + body
            new_md = body + '\n' + row
        else:
            new_md = TABLE_HEADER + '\n' + row
        ok = _put_file('paper_trading_log.md', new_md, sha,
                       'Trade: ' + str(trade.get('token')) + ' ' + str(trade.get('action')))
        print('paper_trading_log.md pushed:', ok)

    except Exception as e:
        print('push_trade error: ' + str(e))

def load_from_github():
    if not GITHUB_TOKEN:
        return
    try:
        r = requests.get(
            'https://raw.githubusercontent.com/' + REPO + '/main/trade_log.json',
            timeout=10
        )
        if r.status_code == 200:
            trades = r.json()
            with open('trade_log.json', 'w') as f:
                json.dump(trades, f, indent=2)
            print('Loaded ' + str(len(trades)) + ' trades from GitHub')
    except Exception as e:
        print('load_from_github error: ' + str(e))
