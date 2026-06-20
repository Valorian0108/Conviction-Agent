import requests, os

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

_last_alert_tokens = set()  # dedup: only alert when signal tokens change

def send_alert(results, summary):
    global _last_alert_tokens
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print('No Telegram credentials'); return
    if not results:
        return

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

    message_text = '\n'.join(lines)

    try:
        r = requests.post(
            'https://api.telegram.org/bot' + TELEGRAM_TOKEN + '/sendMessage',
            json={'chat_id': TELEGRAM_CHAT_ID, 'text': message_text},
            timeout=10
        )
        if r.status_code == 200:
            print('Telegram alert sent for: ' + ', '.join(current_tokens))
        else:
            print('Telegram error: ' + str(r.status_code))
    except Exception as e:
        print('Telegram failed: ' + str(e))
