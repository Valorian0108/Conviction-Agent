from flask import Flask, render_template_string, jsonify
import json, os, requests
from github_watcher import scan as gscan
from governance_watcher import scan as govscan
from conviction import score
from ai_reasoning import reason
from notifier import send_alert
import bot
from github_logger import load_from_github
try:
    load_from_github()
except Exception as _e:
    print('WARNING: load_from_github failed: ' + str(_e))

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
h2{color:#ffffff;font-size:.95em;margin:32px 0 12px;text-transform:uppercase;letter-spacing:3px;border-bottom:1px solid #30363d;padding-bottom:8px}
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
<div style="display:flex;gap:12px;flex-wrap:wrap;margin:16px 0">
  <div class="card" style="flex:1;min-width:120px;text-align:center;padding:12px">
    <div style="color:#8b949e;font-size:.75em">PORTFOLIO</div>
    <div style="color:#f0883e;font-size:1.4em;font-weight:bold" id="stat-balance">${{ current_balance }}</div>
    <div style="color:#8b949e;font-size:.7em">SIM</div>
  </div>
  <div class="card" style="flex:1;min-width:120px;text-align:center;padding:12px">
    <div style="color:#8b949e;font-size:.75em">TRADES</div>
    <div style="color:#3fb950;font-size:1.4em;font-weight:bold" id="stat-trades">{{ trades|length }}</div>
    <div style="color:#8b949e;font-size:.7em">EXECUTED</div>
  </div>
  <div class="card" style="flex:1;min-width:120px;text-align:center;padding:12px">
    <div style="color:#8b949e;font-size:.75em">SIGNALS</div>
    <div style="color:#58a6ff;font-size:1.4em;font-weight:bold" id="stat-signals">{{ results|length }}</div>
    <div style="color:#8b949e;font-size:.7em">ACTIVE NOW</div>
  </div>
  <div class="card" style="flex:1;min-width:120px;text-align:center;padding:12px">
    <div style="color:#8b949e;font-size:.75em">PROTOCOLS</div>
    <div style="color:#e6edf3;font-size:1.4em;font-weight:bold">13</div>
    <div style="color:#8b949e;font-size:.7em">WATCHING</div>
  </div>
</div>
<a href="https://t.me/conviction_agent_demi_bot" target="_blank" 
   style="display:inline-block;background:#1f6feb;color:#fff;padding:8px 20px;border-radius:6px;text-decoration:none;font-size:.85em;margin-bottom:16px">
  ✈ Message the Bot on Telegram
</a>
</div>

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
{% if trades %}
{% for t in trades %}
<div class="card trade-item" {% if loop.index > 10 %}style="display:none"{% endif %}>
  <div><b style="color:#58a6ff">{{ t.action }} {{ t.token }}</b>
  <span style="color:#e6edf3"> @ ${{ t.price }}</span>
  <span class="sim">SIM</span></div>
  <div class="meta">${{ t.usd_amount }} | {{ t.quantity }} units | Conviction {{ t.conviction }}/5</div>
  <div class="meta">{{ t.timestamp }}</div>
</div>
{% endfor %}
{% if trades|length > 10 %}
<button id="loadbtn" onclick="loadMore()" style="width:100%;padding:12px;margin-top:8px;background:#21262d;border:1px solid #30363d;color:#58a6ff;border-radius:6px;cursor:pointer;font-family:monospace;font-size:.9em">
  Show More ({{ trades|length - 10 }} more trades)
</button>
<script>
var _expanded = false;
function loadMore() {
  var items = document.querySelectorAll('.trade-item');
  var btn = document.getElementById('loadbtn');
  if (!_expanded) {
    for (var i = 0; i < items.length; i++) { items[i].style.display = ''; }
    btn.textContent = 'Show Less';
    _expanded = true;
  } else {
    for (var i = 10; i < items.length; i++) { items[i].style.display = 'none'; }
    btn.textContent = 'Show More ({{ trades|length - 10 }} more trades)';
    _expanded = false;
  }
}
</script>
{% endif %}
{% else %}
<div class="card"><div class="empty">No trades yet.</div></div>
{% endif %}

<h2>Protocol Monitor</h2>
<div id="protocols" class="card">Loading...</div>
<h2>Live Prices</h2>
<div id="prices" class="card" style="display:flex;flex-wrap:wrap;gap:16px;align-items:center">Loading...</div>
<script>
function updateData() {
  fetch('/api/status').then(r=>r.json()).then(d=>{
    if (d.balance) document.getElementById('stat-balance').textContent = '$' + d.balance;
    if (d.trade_count !== undefined) document.getElementById('stat-trades').textContent = d.trade_count;
    if (d.signals !== undefined) document.getElementById('stat-signals').textContent = d.signals;
    let h = '';
    d.github.forEach(p=>{
      let w = p.score>0?(p.score/3)*100:8;
      let c = p.score>=2?'#f0883e':p.score>=1?'#58a6ff':'#30363d';
      h += '<div style="display:flex;align-items:center;gap:12px;margin:6px 0">';
      h += '<span style="width:90px;color:#8b949e;font-size:.85em">'+p.protocol+'</span>';
      h += '<div style="flex:1;background:#21262d;border-radius:4px;height:8px">';
      h += '<div style="width:'+w+'%;background:'+c+';height:8px;border-radius:4px;transition:width .5s"></div></div>';
      h += '<span style="color:'+c+';font-size:.8em;width:30px">'+p.score+'/3</span></div>';
    });
    document.getElementById('protocols').innerHTML = h||'Scanning...';
  }).catch(()=>{});
  fetch('/api/prices').then(r=>r.json()).then(d=>{
    let h = '';
    Object.entries(d).forEach(([k,v])=>{
      h += '<div style="text-align:center;padding:8px 16px;background:#21262d;border-radius:6px">';
      h += '<div style="color:#8b949e;font-size:.75em">'+k+'</div>';
      h += '<div style="color:#58a6ff;font-weight:bold;font-size:1.1em">$'+parseFloat(v).toFixed(4)+'</div></div>';
    });
    document.getElementById('prices').innerHTML = h || 'Unavailable';
  }).catch(()=>{});
}
updateData();
setInterval(updateData, 30000);
</script>
<div style="background:#161b22;border:1px solid #30363d;border-radius:8px;padding:20px;margin:32px 0">
  <div style="color:#58a6ff;font-size:.8em;letter-spacing:2px;margin-bottom:8px">ABOUT</div>
  <div style="color:#e6edf3;font-size:.9em;line-height:1.6">
    Conviction Agent is an autonomous AI trading agent. It monitors 13 crypto protocol GitHub repositories 
    and Snapshot governance proposals for unusual activity. Qwen AI analyzes all signals and decides 
    whether to trade. When conviction crosses the threshold, a sim trade executes on Bitget at live prices.
  </div>
  <div style="color:#8b949e;font-size:.8em;margin-top:8px">
    Bitget AI Hackathon S1 &mdash; Track 1: Trading Agent &mdash; Signals: GitHub dev activity + governance &mdash; Execution: Bitget spot sim
  </div>
</div>

<h2>Scan Log</h2>
<div id="scan-meta" style="color:#8b949e;font-size:.8em;margin-bottom:8px">Loading...</div>
<div id="scan-log" style="background:#0d1117;border:1px solid #30363d;border-radius:8px;padding:16px;font-family:'Courier New',monospace;font-size:.78em;color:#8b949e;max-height:340px;overflow-y:auto;white-space:pre-wrap">Waiting for scan data...</div>
<script>
function loadLogs() {
  fetch('/api/logs').then(function(r){return r.json();}).then(function(d){
    var el = document.getElementById('scan-log');
    var meta = document.getElementById('scan-meta');
    if (d.log && d.log.length > 0) {
      var html = d.log.map(function(line) {
        if (line.includes('EXECUTOR') || line.includes('[SIM]')) return '<span style="color:#3fb950">' + line + '</span>';
        if (line.includes('Qwen') || line.includes('AI')) return '<span style="color:#58a6ff">' + line + '</span>';
        if (line.includes('ERROR') || line.includes('error') || line.includes('failed')) return '<span style="color:#f85149">' + line + '</span>';
        if (line.includes('Skipping') || line.includes('cooldown')) return '<span style="color:#f0883e">' + line + '</span>';
        return '<span>' + line + '</span>';
      }).join('\n');
      el.innerHTML = html;
      el.scrollTop = el.scrollHeight;
      meta.textContent = 'Scan #' + d.scan_count + ' completed ' + d.ts;
    } else {
      el.textContent = 'First scan runs at startup and then every 30 min. Check back shortly.';
      meta.textContent = 'Last scan: ' + (d.ts || 'pending');
    }
  }).catch(function(){
    document.getElementById('scan-log').textContent = 'Log unavailable';
  });
}
loadLogs();
setInterval(loadLogs, 15000);
</script>

<div class="footer"></div>
</body></html>"""


import threading, time, datetime

_cache = {'results': [], 'summary': '', 'trades': [], 'ts': 'Not yet scanned', 'scan_log': [], 'scan_count': 0}

if os.path.exists('trade_log.json'):
    try:
        with open('trade_log.json') as _f:
            _cache['trades'] = list(reversed(json.load(_f)))
    except Exception:
        pass

def _log(lines, entry):
    lines.append(entry)
    print(entry)

def _bg_scan():
    while True:
        lines = []
        try:
            _log(lines, '--- SCAN START ' + datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC') + ' ---')

            _log(lines, 'Scanning GitHub activity...')
            from github_watcher import WATCHED_REPOS, score_repo as _sr
            all_gh = []
            for r in WATCHED_REPOS:
                result = _sr(r)
                all_gh.append(result)
                reasons = ' | '.join(result['reasons']) if result['reasons'] else 'no unusual activity'
                _log(lines, '  ' + result['protocol'].ljust(12) + ' score ' + str(result['score']) + '/3  ' + reasons)

            _cache['github_scores'] = [{'protocol': r['protocol'], 'score': r['score']} for r in all_gh]
            gh = [r for r in all_gh if r['score'] > 0]
            _log(lines, 'GitHub signals: ' + str(len(gh)) + ' protocols above threshold')

            _log(lines, 'Scanning governance...')
            gov = govscan()
            _log(lines, 'Governance signals: ' + str(len(gov)))

            _log(lines, 'Calling Qwen AI...')
            ai = reason(gh, gov)
            if ai:
                _log(lines, 'Qwen AI responded — ' + str(len(ai.get('trades', []))) + ' trade(s) suggested')
                if ai.get('summary'):
                    _log(lines, 'AI summary: ' + ai['summary'][:120])
                _cache['results'] = ai['trades']
                _cache['summary'] = ai['summary']
            else:
                _log(lines, 'Qwen AI unavailable — using fallback scorer')
                _cache['results'] = score(gh, gov)
                _cache['summary'] = ''

            _log(lines, 'EXECUTOR - Processing ' + str(len(_cache['results'])) + ' signal(s)...')
            from executor import run as _r
            trades_made = _r(_cache['results'])
            _log(lines, str(len(trades_made)) + ' trade(s) executed this cycle')
            for t in trades_made:
                _log(lines, '  [SIM] ' + t['action'] + ' ' + t['token'] + ' @ $' + str(t['price']) + ' | $' + str(t['usd_amount']) + ' | conviction ' + str(t['conviction']) + '/5')

            if os.path.exists('trade_log.json'):
                with open('trade_log.json') as f:
                    _cache['trades'] = list(reversed(json.load(f)))

            if _cache['results']:
                send_alert(_cache['results'], _cache['summary'])

            tokens = ['BTCUSDT', 'ETHUSDT', 'OPUSDT', 'STRKUSDT', 'ZKUSDT', 'LINKUSDT', 'ARBUSDT']
            prices = {}
            for t in tokens:
                try:
                    pr = requests.get('https://api.bitget.com/api/v2/spot/market/tickers',
                        params={'symbol': t}, timeout=5)
                    if pr.status_code == 200:
                        data = pr.json().get('data', [])
                        if data:
                            prices[t.replace('USDT', '')] = data[0]['lastPr']
                except:
                    pass
            _cache['prices'] = prices

            _cache['ts'] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
            _log(lines, '--- SCAN COMPLETE ' + _cache['ts'] + ' | next in 30min ---')

        except Exception as e:
            _log(lines, 'ERROR: ' + str(e))
            _cache['ts'] = 'Error: ' + str(e)

        finally:
            _cache['scan_count'] = _cache.get('scan_count', 0) + 1
            _cache['scan_log'] = lines[-150:]

        time.sleep(1800)

try:
    bot.start()
except Exception as _e:
    print('WARNING: Telegram bot failed to start: ' + str(_e))

try:
    _t = threading.Thread(target=_bg_scan, daemon=True)
    _t.start()
except Exception as _e:
    print('WARNING: Background scan failed to start: ' + str(_e))

@app.route('/')
def index():
    trades = _cache['trades']
    if trades:
        current_balance = trades[0].get('balance_after', 10000)
    else:
        current_balance = 10000
    return render_template_string(HTML, results=_cache['results'], trades=trades,
                                  summary=_cache['summary'],
                                  current_balance='{:,.2f}'.format(current_balance))

@app.route('/health')
def health():
    return 'ok'

@app.route('/api/status')
def api_status():
    trades = _cache.get('trades', [])
    balance = trades[0].get('balance_after', 10000) if trades else 10000
    return jsonify({
        'github': _cache.get('github_scores', []),
        'signals': len(_cache['results']),
        'trade_count': len(trades),
        'balance': '{:,.2f}'.format(balance)
    })

@app.route('/api/prices')
def api_prices():
    tokens = ['BTCUSDT', 'ETHUSDT', 'OPUSDT', 'LINKUSDT', 'ARBUSDT', 'STRKUSDT']
    cached = _cache.get('prices', {})
    if cached:
        return jsonify(cached)
    prices = {}
    for t in tokens:
        try:
            r = requests.get('https://api.bitget.com/api/v2/spot/market/tickers',
                params={'symbol': t}, timeout=10)
            if r.status_code == 200:
                d = r.json().get('data', [])
                if d:
                    prices[t.replace('USDT', '')] = d[0]['lastPr']
        except:
            pass
    return jsonify(prices)

@app.route('/api/signals')
def api_signals():
    gh = gscan()
    gov = govscan()
    return jsonify(score(gh, gov))

@app.route('/api/logs')
def api_logs():
    return jsonify({
        'log': _cache.get('scan_log', []),
        'scan_count': _cache.get('scan_count', 0),
        'ts': _cache.get('ts', 'Not yet scanned')
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
