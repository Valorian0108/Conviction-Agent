import requests, json, re, os

QWEN_API_KEY = os.getenv('QWEN_API_KEY', '')
QWEN_BASE_URL = 'https://hackathon.bitgetops.com/v1'
MODEL = 'qwen3.6-plus'

def build_prompt(github_signals, gov_signals):
    lines = [
        'You are an autonomous crypto trading agent. Analyze these signals and decide whether to trade.',
        '',
        'DEVELOPER ACTIVITY SIGNALS:'
    ]
    active = [s for s in github_signals if s['score'] > 0]
    if active:
        for s in active:
            lines.append('- ' + s['protocol'] + ' score ' + str(s['score']) + '/3: ' + ' | '.join(s['reasons']))
    else:
        lines.append('- No unusual developer activity')
    lines.append('')
    lines.append('GOVERNANCE SIGNALS:')
    if gov_signals:
        for s in gov_signals:
            lines.append('- ' + s['protocol'] + ': ' + s['title'] + ' (' + str(s['votes']) + ' votes)')
    else:
        lines.append('- No active governance proposals')
    lines.append('')
    lines.append('Respond ONLY with valid JSON, no other text:')
    lines.append('{"trades":[{"token":"OPUSDT","action":"BUY","size_pct":5,"conviction":3,"reasoning":"your reasoning"}],"market_summary":"overall view"}')
    lines.append('Only include trades you are confident about. Empty trades array if no opportunity.')
    return '\n'.join(lines)

def call_qwen(prompt):
    if not QWEN_API_KEY:
        print('No Qwen API key set'); return None
    try:
        r = requests.post(
            QWEN_BASE_URL + '/chat/completions',
            headers={'Content-Type':'application/json','Authorization':'Bearer ' + QWEN_API_KEY},
            json={'model': MODEL, 'messages': [{'role':'user','content':prompt}], 'max_tokens': 800},
            timeout=30
        )
        if r.status_code == 200:
            return r.json()['choices'][0]['message']['content']
        print('Qwen error: ' + str(r.status_code))
        return None
    except Exception as e:
        print('Qwen failed: ' + str(e)); return None

def reason(github_signals, gov_signals):
    print('Calling Qwen AI...')
    content = call_qwen(build_prompt(github_signals, gov_signals))
    if not content:
        return None
    try:
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            result = json.loads(match.group())
            trades = []
            for t in result.get('trades', []):
                trades.append({
                    'token': t.get('token',''),
                    'action': t.get('action','BUY'),
                    'size_pct': t.get('size_pct', 4),
                    'conviction': t.get('conviction', 2),
                    'reason': t.get('reasoning','AI signal'),
                    'ai_powered': True
                })
            return {'trades': trades, 'summary': result.get('market_summary','')}
    except Exception as e:
        print('Parse error: ' + str(e))
    return None
