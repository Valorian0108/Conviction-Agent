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
        # Also push trade_log.json
        try:
            import json as _j
            with open('trade_log.json') as _f:
                raw = _j.load(_f)
            _, sha2 = None, None
            r2 = requests.get(f'{API_BASE}/repos/{GITHUB_REPO}/contents/trade_log.json', headers=headers, timeout=10)
            if r2.status_code == 200:
                sha2 = r2.json().get('sha')
            enc2 = base64.b64encode(_j.dumps(raw, indent=2).encode()).decode()
            p2 = {'message': 'Update trade_log.json', 'content': enc2}
            if sha2: p2['sha'] = sha2
            requests.put(f'{API_BASE}/repos/{GITHUB_REPO}/contents/trade_log.json', headers=headers, json=p2, timeout=15)
        except Exception as _e:
            print('trade_log.json push failed: ' + str(_e))
    except Exception as e:
        print('GitHub push failed: ' + str(e))

def load_from_github():
    if not GITHUB_TOKEN:
        return
    try:
        current, sha = get_file()
        if current and os.path.exists('trade_log.json'):
            return
        if current:
            import json
            lines = [l for l in current.split('\n') if l.startswith('|') and 'Timestamp' not in l and '---' not in l and l.strip() != '|']
            trades = []
            for line in lines:
                parts = [p.strip() for p in line.split('|')[1:-1]]
                if len(parts) >= 9:
                    try:
                        trades.append({
                            'timestamp': parts[0],
                            'token': parts[1],
                            'action': parts[2],
                            'price': float(parts[3].replace('$','')),
                            'quantity': float(parts[4]),
                            'usd_amount': float(parts[5].replace('$','')),
                            'balance_before': float(parts[6].replace('$','')),
                            'balance_after': float(parts[7].replace('$','')),
                            'conviction': int(parts[8].replace('/5','')),
                            'mode': 'SIM'
                        })
                    except: pass
            if trades:
                with open('trade_log.json', 'w') as f:
                    json.dump(trades, f, indent=2)
                print('Loaded ' + str(len(trades)) + ' trades from GitHub')
    except Exception as e:
        print('Load from GitHub failed: ' + str(e))

