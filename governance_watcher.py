import requests
SNAPSHOT_API = 'https://hub.snapshot.org/graphql'
WATCHED_SPACES = ['uniswap','aave.eth','arbitrumfoundation.eth','optimismfoundation.eth','ens.eth']

def get_active_proposals(space):
    q = '{proposals(where:{space:\"%s\",state:\"active\"},first:5){title votes quorum scores_total}}' % space
    try:
        r = requests.post(SNAPSHOT_API, json={'query':q}, timeout=10)
        return r.json().get('data',{}).get('proposals',[]) if r.status_code==200 else []
    except: return []

def scan():
    print('Scanning governance...'); signals=[]
    for space in WATCHED_SPACES:
        props = get_active_proposals(space)
        for p in props:
            if p.get('votes',0) > 50:
                signals.append({'protocol':space,'title':p['title'][:50],'votes':p['votes']})
                print(f"  {space}: {p['title'][:50]} — {p['votes']} votes")
    print(f'Active governance signals: {len(signals)}'); return signals

