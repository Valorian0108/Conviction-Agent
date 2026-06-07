import requests, os

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

def send_alert(results, summary):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print('No Telegram credentials'); return
    if not results:
        return

    lines = ['CONVICTION AGENT - Signal Alert', '']
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
            json={'chat_id': TELEGRAM_CHAT_ID, 'text': '\n'.join(lines)},
            timeout=10
        )
        if r.status_code == 200:
            print('Telegram alert sent')
        else:
            print('Telegram error: ' + str(r.status_code))
    except Exception as e:
        print('Telegram failed: ' + str(e))
