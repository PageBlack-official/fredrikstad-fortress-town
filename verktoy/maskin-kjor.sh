#!/bin/sh
# Regelsjekken på Vegars Mac mini (Vegars-Plex.local), med ekte skjermkort i stedet for SwiftShader i skyen.
# Oppsett én gang: ~/sot-maskin/ har node/ (Node 22), py/ (Python 3.12 via uv) og repo/ (klonen). Se LESMEG «Regler på Mac-en».
# Bruk (fra iMac-en):  ssh Vegars-Plex.local 'sh ~/sot-maskin/repo/verktoy/maskin-kjor.sh [gren-eller-commit] [regelnr …]'
# Kjører i bakgrunnen; følg med i ~/sot-maskin/kjor.log. Ferdig når siste linje er «FERDIG <hash>».
set -e
M="$HOME/sot-maskin"; R="$M/repo"
export PATH="$M/py/bin:$M/node/bin:$PATH" PW_GPU=1 PYTHONPATH="$R/regler"
REF="${1:-origin/funk/brukeropplevelse}"; [ $# -gt 0 ] && shift
cd "$R"
git fetch -q origin
git checkout -q --detach "$REF" 2>/dev/null || git checkout -q --detach "origin/$REF"
git clean -qfd -- rapport ut 2>/dev/null || true; git checkout -q -- rapport ut 2>/dev/null || true
[ -d node_modules/esbuild ] || npm install --no-audit --no-fund >/dev/null
# referanser som ikke ligger i git: Google-flyfotoet (ut av git i 5b09956, hentes fra historikken) og kommunens ortofotofliser (lisens ikke avklart)
F=kilder/flyfoto-google-2026-10-23.jpg; [ -s "$F" ] || git show 5b09956^:$F > "$F"
python3 - <<'PY'
import json, os, sys
sys.path[:0] = ['verktoy', 'regler']
import flater
m = json.load(open('kilder/ortofoto-2024/ortofoto-2024.json'))
mangler = [f for f in m['fliser'] if not os.path.exists(os.path.join('kilder/ortofoto-2024', f['fil']))]
for f in mangler:
    x0, y0, x1, y1 = f['x0'], f['y0'], f['x1'], f['y1']
    flater.hent_fliser((x0, y0, x1, y1))
print('ortofoto: hentet', len(mangler), 'fliser')
PY
python3 regler/kjor.py "$@"
echo "FERDIG $(git log -1 --format=%h -- src data regler bygg.py datalag.py assets)"
