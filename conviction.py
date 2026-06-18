TOKEN_MAP = {
    'Uniswap': 'UNIUSDT',
    'Aave': 'AAVEUSDT',
    'Arbitrum': 'ARBUSDT',
    'Optimism': 'OPUSDT',
    'Chainlink': 'LINKUSDT',
    'Curve': 'CRVUSDT',
    'MakerDAO': 'MKRUSDT',
    'zkSync': 'ZKUSDT',
    'Scroll': 'SCRUSDT',
    'Polygon': 'POLUSDT',
    'EigenLayer': 'EIGENUSDT',
    'Starknet': 'STRKUSDT',
    'Base': 'ETHUSDT',
    'uniswap': 'UNIUSDT',
    'aave.eth': 'AAVEUSDT',
    'arbitrumfoundation.eth': 'ARBUSDT',
    'optimismfoundation.eth': 'OPUSDT',
    'ens.eth': 'ENSUDT'
}

def score(github_signals, gov_signals):
    scores = {}
    for s in github_signals:
        p = s['protocol']
        scores[p] = scores.get(p, 0) + s['score']
    for s in gov_signals:
        p = s['protocol']
        scores[p] = scores.get(p, 0) + s.get('score', 1)
    results = []
    for protocol, total in scores.items():
        token = TOKEN_MAP.get(protocol)
        if not token:
            continue
        conviction = min(total, 5)
        if conviction >= 2:
            results.append({
                'protocol': protocol,
                'token': token,
                'conviction': conviction,
                'action': 'BUY',
                'size_pct': conviction * 2,
                'reason': 'Conviction ' + str(conviction) + '/5 - dev and governance signals aligned'
            })
    results.sort(key=lambda x: x['conviction'], reverse=True)
    return results

def display(results):
    if not results:
        print('No conviction signals above threshold.')
        return
    print('CONVICTION ENGINE')
    for r in results:
        bar = '*' * r['conviction']
        print('  ' + r['token'] + ' [' + bar + '] ' + str(r['conviction']) + '/5 -> ' + r['action'] + ' ' + str(r['size_pct']) + '% of portfolio')
        print('  ' + r['reason'])
