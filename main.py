import time
from datetime import datetime, timezone
from github_watcher import scan as gscan
from governance_watcher import scan as govscan
from conviction import score, display
from executor import run

SCAN_INTERVAL = 1800

def main():
    print('CONVICTION AGENT STARTED')
    cycle = 0
    while True:
        cycle += 1
        now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
        print('--- CYCLE ' + str(cycle) + ' | ' + now + ' ---')
        gh = gscan()
        gov = govscan()
        results = score(gh, gov)
        display(results)
        run(results)
        print('Next scan in 30 minutes...')
        time.sleep(SCAN_INTERVAL)

if __name__ == '__main__':
    main()
