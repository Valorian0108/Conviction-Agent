import requests, os, base64, json
from datetime import datetime, timezone

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
GITHUB_REPO = 'Valorian0108/Conviction-Agent'
FILE_PATH = 'paper_trading_log.md'
API_BASE = 'https://api.github.com'

def get_file():
    headers = {'Authorization': 'token ' + GITHUB_TOKEN}
    r = requests.get(f'{API_BASE}/repos/{GITHUB_REPO}/contents/{FILE_PATH}', headers=headers, timeout=10)
    if r.status_code == 200:
        data = r.json()
        content = base64.b64decode(data['content']).decode('utf-8')
        return content, data['sha']
    return None, None

def push_trade(trade):
    if not GITHUB_TOKEN:
        return
    try:
        current, sha = get_file()
        row = (
            '| ' + trade.get('timestamp', '')[:19].replace('T', ' ') +
            ' | ' + trade.get('token', '') +
            ' | ' + trade.get('action', '') +
            ' | $' + str(trade.get('price', '')) +
            ' | ' + str(trade.get('quantity', '')) +
            ' | $' + str(trade.get('usd_amount', '')) +
            ' | $' + str(trade.get('balance_before', '')) +
            ' | $' + str(trade.get('balance_after', '')) +
            ' | ' + str(trade.get('conviction', '')) + '/5 |'
        )
        if current:
            new_content = current + '\n' + row
        else:
            header = '# Paper Trading Log - Conviction Agent\n\n'
            header += 'Sim portfolio: $10,000 | Mode: SIM | Exchange: Bitget\n\n'
            header += '| Timestamp | Pair | Direction | Price | Quantity | Amount | Balance Before | Balance After | Conviction |\n'
            header += '|-----------|------|-----------|-------|----------|--------|----------------|---------------|------------|\n'
            new_content = header + row
        encoded = base64.b64encode(new_content.encode('utf-8')).decode('utf-8')
        payload = {
            'message': 'Trade log: ' + trade.get('token', '') + ' ' + trade.get('action', '') + ' @ $' + str(trade.get('price', '')),
            'content': encoded
        }
        if sha:
            payload['sha'] = sha
        headers = {'Authorization': 'token ' + GITHUB_TOKEN, 'Content-Type': 'application/json'}
        requests.put(f'{API_BASE}/repos/{GITHUB_REPO}/contents/{FILE_PATH}', headers=headers, json=payload, timeout=15)
        print('Trade pushed to GitHub')
    except Exception as e:
        print('GitHub push failed: ' + str(e))
