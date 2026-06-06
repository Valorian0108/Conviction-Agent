import os, json, requests
from datetime import datetime, timezone

BASE_URL = 'https://api.bitget.com'
SIM_PORTFOLIO = 10000
trade_log = []

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
    price = get_price(token)
    if not price:
        print('  Could not get price for ' + token)
        return None
    usd_amount = SIM_PORTFOLIO * (size_pct / 100)
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
        'mode': 'SIM'
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
        with open('trade_log.json', 'w') as f:
            json.dump(trade_log, f, indent=2)
        print(str(len(trades)) + ' trades logged to trade_log.json')
    return trades
