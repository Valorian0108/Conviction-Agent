import os, json, requests, time as _time
from github_logger import push_trade
from datetime import datetime, timezone

BASE_URL = 'https://api.bitget.com'
SIM_PORTFOLIO = 10000
COOLDOWN_FILE = 'cooldown.json'

def get_current_balance():
    if not os.path.exists('trade_log.json'):
        return SIM_PORTFOLIO
    try:
        with open('trade_log.json') as f:
            trades = json.load(f)
        if not trades:
            return SIM_PORTFOLIO
        last = sorted(trades, key=lambda x: x.get('timestamp', ''))[-1]
        return last.get('balance_after', SIM_PORTFOLIO)
    except:
        return SIM_PORTFOLIO

trade_log = []

def _load_cooldown():
    try:
        if os.path.exists(COOLDOWN_FILE):
            with open(COOLDOWN_FILE) as f:
                return json.load(f)
    except:
        pass
    return {}

def _save_cooldown(cd):
    try:
        with open(COOLDOWN_FILE, 'w') as f:
            json.dump(cd, f)
    except:
        pass

def get_price(symbol):
    try:
        r = requests.get(f'{BASE_URL}/api/v2/spot/market/tickers',
                        params={'symbol': symbol}, timeout=10)
        if r.status_code == 200:
            data = r.json().get('data', [])
            if data:
                return float(data[0]['lastPr'])
    except:
        pass
    return None

def execute_trade(token, action, size_pct, conviction, reason):
    now = _time.time()
    _last_traded = _load_cooldown()
    if token in _last_traded and now - _last_traded[token] < 1800:
        mins_ago = int((now - _last_traded[token]) / 60)
        print(f'  Skipping {token} - traded {mins_ago}m ago (cooldown 30m)')
        return None
    _last_traded[token] = now
    _save_cooldown(_last_traded)

    price = get_price(token)
    if not price:
        print('  Could not get price for ' + token)
        return None
    current_balance = get_current_balance()
    if current_balance < 500:
        current_balance = 10000
        print('Portfolio reset to $10,000')
    usd_amount = current_balance * (size_pct / 100)
    quantity = usd_amount / price
    trade = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'token': token,
        'action': action,
        'price': price,
        'usd_amount': round(usd_amount, 2),
        'quantity': round(quantity, 6),
        'conviction': conviction,
        'reason': reason,
        'mode': 'SIM',
        'balance_before': round(current_balance, 2),
        'balance_after': round(current_balance + usd_amount if action == 'SELL' else current_balance - usd_amount, 2),
        'balance_change': round(usd_amount if action == 'SELL' else -usd_amount, 2)
    }
    trade_log.append(trade)
    print('  [SIM] ' + action + ' ' + token + ' @ $' + str(price))
    print('        Amount: $' + str(usd_amount) + ' | Qty: ' + str(round(quantity, 6)))
    return trade

def run(conviction_results):
    print('EXECUTOR - Processing signals...')
    trades = []
    for r in conviction_results:
        if r['conviction'] >= 2:
            trade = execute_trade(r['token'], r['action'],
                                  r['size_pct'], r['conviction'], r['reason'])
            if trade:
                trades.append(trade)
    if trades:
        existing = []
        if os.path.exists('trade_log.json'):
            try:
                with open('trade_log.json') as f:
                    existing = json.load(f)
            except Exception:
                existing = []
        all_trades = existing + trades
        with open('trade_log.json', 'w') as f:
            json.dump(all_trades, f, indent=2)
        print(str(len(trades)) + ' trades logged to trade_log.json')
        try:
            from github_logger import push_trade
            for t in trades:
                push_trade(t)
        except Exception as e:
            print('GitHub push error: ' + str(e))
    return trades
