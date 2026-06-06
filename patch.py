content = open('app.py').read()
old = "    gh = gscan()\n    gov = govscan()\n    results = score(gh, gov)"
new = "    gh = gscan()\n    gov = govscan()\n    ai = reason(gh, gov)\n    results = ai['trades'] if ai and ai['trades'] else score(gh, gov)\n    summary = ai['summary'] if ai else ''"
content = content.replace(old, new)
old2 = "return render_template_string(HTML, results=results, trades=trades)"
new2 = "return render_template_string(HTML, results=results, trades=trades, summary=summary)"
content = content.replace(old2, new2)
open('app.py', 'w').write(content)
print('Done')
