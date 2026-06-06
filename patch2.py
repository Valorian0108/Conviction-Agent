content = open('app.py').read()
old = '<h2>Active Signals</h2>'
new = '''{% if summary %}
<div class="card" style="border-left:3px solid #1f6feb;margin-bottom:16px">
  <div style="color:#58a6ff;font-size:.8em;margin-bottom:6px">QWEN AI ASSESSMENT</div>
  <div>{{ summary }}</div>
</div>
{% endif %}
<h2>Active Signals</h2>'''
content = content.replace(old, new)
open('app.py', 'w').write(content)
print('Done')
