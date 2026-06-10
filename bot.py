import requests, os, time, threading
from executor import execute_trade
from github_watcher import scan as gscan
from governance_watcher import scan as govscan
from ai_reasoning import reason
from conviction import score

TOKEN = os.getenv('TELEGRAM_TOKEN', '')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
BASE = 'https://api.telegram.org/bot' + TOKEN

_threshold = [2]
_last_update_id = [0]

def send(text):
    try:
        requests.post(BASE + '/sendMessage',
            json={'chat_id': CHAT_ID, 'text': text}, timeout=10)
    except: pass

def handle(text):
    text = text.strip().lower()

    if text == '/start' or text == '/start@conviction_agent_demi_bot':
        send('Conviction Agent\n\nI monitor 13 crypto protocols for unusual developer activity and governance signals. Qwen AI analyzes everything and executes trades when conviction is high.\n\n/scan - scan all 13 protocols now\n/prices - live token prices\n/status - agent health check\n/trade OPUSDT - force a sim trade\n/threshold 2 - set conviction level\n/help - show all commands')
        return

    if text == '/scan':
        send('Scanning 13 protocols...')
        gh = gscan()
        gov = govscan()
        ai = reason(gh, gov)
        results = ai['trades'] if ai and ai['trades'] else score(gh, gov)
        summary = ai['summary'] if ai else ''
        if results:
            msg = 'SIGNALS FOUND\n\n'
            for r in results:
                msg += r['token'] + ' - ' + r['action'] + '\n'
                msg += 'Conviction: ' + str(r['conviction']) + '/5\n'
                msg += r['reason'] + '\n\n'
        else:
            msg = 'Scan complete. No signals above threshold.\n\n'
        if summary:
            msg += 'Qwen AI: ' + summary[:300]
        send(msg)

    elif text.startswith('/trade '):
        token = text.split(' ')[1].upper()
        if not token.endswith('USDT'):
            token = token + 'USDT'
        send('Executing sim trade for ' + token + '...')
        trade = execute_trade(token, 'BUY', 4, 2, 'Manual trade via Telegram')
        if trade:
            send('Trade executed\n' + token + ' @ $' + str(trade['price']) + '\nAmount: $' + str(trade['usd_amount']))
        else:
            send('Could not get price for ' + token)

    elif text.startswith('/threshold '):
        try:
            n = int(text.split(' ')[1])
            _threshold[0] = n
            send('Conviction threshold set to ' + str(n) + '/5')
        except:
            send('Usage: /threshold 2')

    elif text == '/status':
        from app import _cache
        ts = _cache.get('ts', 'Not yet scanned')
        results = _cache.get('results', [])
        trades = _cache.get('trades', [])
        msg = 'STATUS\n\nLast scan: ' + ts + '\nActive signals: ' + str(len(results)) + '\nTrades logged: ' + str(len(trades))
        send(msg)

    elif text == '/prices':
        tokens = ['BTCUSDT','ETHUSDT','OPUSDT','LINKUSDT','STRKUSDT','ZKUSDT','ARBUSDT']
        send('Fetching prices...')
        lines = ['LIVE PRICES\n']
        for t in tokens:
            try:
                r = requests.get('https://api.bitget.com/api/v2/spot/market/tickers',
                                params={'symbol': t}, timeout=5)
                if r.status_code == 200:
                    data = r.json().get('data', [])
                    if data:
                        price = data[0]['lastPr']
                        lines.append(t.replace('USDT','') + ': $' + price)
            except: pass
        send('\n'.join(lines))

    elif text == '/help':
        send('/scan - scan all protocols now\n/trade STRKUSDT - force a sim trade\n/threshold 2 - set conviction level\n/status - agent health check\n/prices - live token prices')

def poll():
    while True:
        try:
            r = requests.get(BASE + '/getUpdates',
                params={'offset': _last_update_id[0] + 1, 'timeout': 30},
                timeout=35)
            if r.status_code == 200:
                updates = r.json().get('result', [])
                for u in updates:
                    _last_update_id[0] = u['update_id']
                    msg = u.get('message', {}).get('text', '')
                    if msg:
                        handle(msg)
        except: pass
        time.sleep(1)

def start():
    t = threading.Thread(target=poll, daemon=True)
    t.start()
