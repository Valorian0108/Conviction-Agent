from flask import Flask, render_template_string, jsonify
import json, os
from github_watcher import scan as gscan
from governance_watcher import scan as govscan
from conviction import score
from notifier import send_alert
from notifier import send_alert
from ai_reasoning import reason

app = Flask(__name__)

HTML = """<!DOCTYPE html>
<html>
<head>
<title>Conviction Agent</title>
<meta http-equiv="refresh" content="300">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Courier New',monospace;background:#0d1117;color:#e6edf3;padding:40px}
h1{color:#58a6ff;font-size:2em;display:inline}
.sub{color:#8b949e;margin:8px 0 32px;font-size:.9em}
.dot{display:inline-block;width:9px;height:9px;background:#3fb950;border-radius:50%;margin-right:8px;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
h2{color:#3fb950;font-size:.95em;margin:32px 0 12px;text-transform:uppercase;letter-spacing:3px}
.card{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:20px;margin-bottom:12px}
.token{font-size:1.6em;color:#f0883e;font-weight:bold}
.badge{background:#1f6feb;padding:2px 10px;border-radius:10px;font-size:.8em;margin-left:8px}
.action{color:#3fb950;font-weight:bold;margin-top:4px}
.reason{color:#8b949e;font-size:.88em;margin-top:8px}
.sim{background:#21262d;border:1px solid #30363d;padding:1px 7px;border-radius:4px;font-size:.8em;color:#8b949e}
.meta{color:#8b949e;font-size:.85em;margin-top:6px}
.empty{color:#8b949e;font-style:italic}
.footer{margin-top:48px;padding-top:16px;border-top:1px solid #21262d;color:#8b949e;font-size:.8em}
</style>
</head>
<body>
<span class="dot"></span><h1>CONVICTION AGENT</h1>
<div class="sub">Bitget AI Hackathon S1 - Track 1 - Refreshes every 5 min</div>

{% if summary %}
<div class="card" style="border-left:3px solid #1f6feb;margin-bottom:16px">
  <div style="color:#58a6ff;font-size:.8em;margin-bottom:6px">QWEN AI ASSESSMENT</div>
  <div>{{ summary }}</div>
</div>
{% endif %}
<h2>Active Signals</h2>
{% if results %}{% for r in results %}
<div class="card">
  <div class="token">{{ r.token }}<span class="badge">{{ r.conviction }}/5</span></div>
  <div class="action">{{ r.action }} {{ r.size_pct }}% of portfolio</div>
  <div class="reason">{{ r.reason }}</div>
</div>
{% endfor %}{% else %}
<div class="card"><div class="empty">No signals above threshold. Agent is watching...</div></div>
{% endif %}

<h2>Trade Log</h2>
{% if trades %}{% for t in trades %}
<div class="card">
  <div><b style="color:#58a6ff">{{ t.action }} {{ t.token }}</b>
  <span style="color:#e6edf3"> @ ${{ t.price }}</span>
  <span class="sim">SIM</span></div>
  <div class="meta">${{ t.usd_amount }} | {{ t.quantity }} units | Conviction {{ t.conviction }}/5</div>
  <div class="meta">{{ t.timestamp }}</div>
</div>
{% endfor %}{% else %}
<div class="card"><div class="empty">No trades yet.</div></div>
{% endif %}

<div class="footer">signals: github dev activity + governance proposals | execution: bitget spot sim</div>
</body></html>"""


import threading, time

_cache = {'results': [], 'summary': '', 'trades': [], 'ts': 'Not yet scanned'}

def _bg_scan():
    while True:
        try:
            gh = gscan()
            gov = govscan()
            ai = reason(gh, gov)
            _cache['results'] = ai['trades'] if ai and ai['trades'] else score(gh, gov)
            _cache['summary'] = ai['summary'] if ai else ''
            if os.path.exists('trade_log.json'):
                with open('trade_log.json') as f:
                    _cache['trades'] = list(reversed(json.load(f)))
            from conviction import score
from notifier import send_alert
from notifier import send_alert as _s
            from executor import run as _r
            _r(_cache['results'])
            if _cache['results']: send_alert(_cache['results'], _cache['summary'])
            if _cache['results']: send_alert(_cache['results'], _cache['summary'])
            import datetime
            _cache['ts'] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
        except Exception as e:
            print('Scan error: ' + str(e))
        time.sleep(1800)

_t = threading.Thread(target=_bg_scan, daemon=True)
_t.start()

@app.route('/')
def index():
    return render_template_string(HTML, results=_cache['results'], trades=_cache['trades'], summary=_cache['summary'])


@app.route('/health')
def health():
    return 'ok'

@app.route('/api/signals')
def api_signals():
    gh = gscan()
    gov = govscan()
    return jsonify(score(gh, gov))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
