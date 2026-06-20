import requests, os
from datetime import datetime, timedelta, timezone

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

def _headers():
    h = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        h["Authorization"] = "Bearer " + GITHUB_TOKEN
    return h

WATCHED_REPOS = [
    {"protocol": "Uniswap",   "repo": "Uniswap/v4-core"},
    {"protocol": "Aave",      "repo": "aave/aave-v3-core"},
    {"protocol": "Arbitrum",  "repo": "OffchainLabs/nitro"},
    {"protocol": "Optimism",  "repo": "ethereum-optimism/optimism"},
    {"protocol": "Chainlink", "repo": "smartcontractkit/chainlink"},
    {"protocol": "Curve",     "repo": "curvefi/curve-contract"},
    {"protocol": "MakerDAO",  "repo": "makerdao/dss"},
    {"protocol": "zkSync",     "repo": "matter-labs/zksync-era"},
    {"protocol": "Scroll",     "repo": "scroll-tech/scroll"},
    {"protocol": "Polygon",    "repo": "0xPolygon/polygon-edge"},
    {"protocol": "EigenLayer", "repo": "Layr-Labs/eigenlayer-contracts"},
    {"protocol": "Starknet",   "repo": "starkware-libs/cairo"},
    {"protocol": "Base",       "repo": "base-org/node"},
]

GITHUB_API = "https://api.github.com"

def get_recent_commits(repo, hours=24):
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    try:
        r = requests.get(f"{GITHUB_API}/repos/{repo}/commits",
                        params={"since": since, "per_page": 100}, headers=_headers(), timeout=10)
        return len(r.json()) if r.status_code == 200 else 0
    except:
        return 0

def get_baseline(repo):
    since = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    try:
        r = requests.get(f"{GITHUB_API}/repos/{repo}/commits",
                        params={"since": since, "per_page": 100}, headers=_headers(), timeout=10)
        return len(r.json()) / 30 if r.status_code == 200 else 1
    except:
        return 1

def get_contributors(repo, hours=48):
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    try:
        r = requests.get(f"{GITHUB_API}/repos/{repo}/commits",
                        params={"since": since, "per_page": 100}, headers=_headers(), timeout=10)
        if r.status_code == 200:
            return len({c["author"]["login"] for c in r.json() if c.get("author")})
        return 0
    except:
        return 0

def score_repo(repo_data):
    repo     = repo_data["repo"]
    protocol = repo_data["protocol"]
    commits  = get_recent_commits(repo)
    baseline = get_baseline(repo)
    contribs = get_contributors(repo)
    score, reasons = 0, []
    ratio = commits / baseline if baseline > 0 else 0
    if ratio >= 3:
        score += 2
        reasons.append(f"{commits} commits today - {ratio:.1f}x normal")
    elif ratio >= 1.5:
        score += 1
        reasons.append(f"{commits} commits today - {ratio:.1f}x normal")
    if contribs >= 5:
        score += 1
        reasons.append(f"{contribs} unique contributors active")
    return {"protocol": protocol, "score": min(score, 3),
            "commits": commits, "contributors": contribs, "reasons": reasons}

def scan():
    print("Scanning GitHub activity...\n")
    results = [score_repo(r) for r in WATCHED_REPOS]
    for r in results:
        print(f"  {r['protocol']:12} score {r['score']}/3  {' | '.join(r['reasons'])}")
    return sorted([r for r in results if r["score"] > 0],
                  key=lambda x: x["score"], reverse=True)

if __name__ == "__main__":
    signals = scan()
    print(f"\nActive signals: {len(signals)}")
