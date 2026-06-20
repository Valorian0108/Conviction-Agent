import requests, os

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

_last_alert_tokens = set()  # dedup: track which tokens we last alerted on

def send_alert(results, summary):
    global _last_alert_tokens
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print('No Telegram credentials'); return
    if not results:
        return

    # Only send if the set of tokens has changed since last alert
    current_tokens = set(r['token'] for r in results)
    if current_tokens == _last_alert_tokens:
        print('No new signals since last alert - skipping Telegram notification')
        return
    _last_alert_tokens = current_tokens

    lines = ['CONVICTION AGENT - New Signal Alert', '']
    for r in results:
        lines.append(r['token'] + ' - ' + r['action'])
        lines.append('Conviction: ' + str(r['conviction']) + '/5')
        lines.append('Size: ' + str(r['size_pct']) + '% of portfolio')
        lines.append('Reason: ' + r['reason'])
        lines.append('')
    if summary:
        lines.append('AI: ' + summary[:250])

    try:
        r = requests.post(
            'https://api.telegram.org/bot' + TELEGRAM_TOKEN + '/sendMessage',
            json={'chat_id': TELEGRAM_CHAT_ID, 'text': '
'.join(lines)},
            timeout=10
        )
        if r.status_code == 200:
            print('Telegram alert sent for: ' + ', '.join(current_tokens))
        else:
            print('Telegram error: ' + str(r.status_code))
    except Exception as e:
        print('Telegram failed: ' + str(e))
