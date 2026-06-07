content = open('app.py').read()

# Fix port for Render
content = content.replace(
    "app.run(host='0.0.0.0', port=5000, debug=False)",
    "app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)"
)

# Add health check route before the main block
health = '''
@app.route('/health')
def health():
    return 'ok'

'''
content = content.replace("@app.route('/api/signals')", health + "@app.route('/api/signals')")

open('app.py', 'w').write(content)
print('Done')
