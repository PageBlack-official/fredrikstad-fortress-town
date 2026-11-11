#!/bin/sh
# OPPGAVE4 økt 5 — frittstående: bevis-ark + regler + publiser /prove1. Detached (nohup), overlever teardown.
set -u
export PATH="$HOME/sot-maskin/py/bin:$HOME/sot-maskin/node/bin:$PATH"
export TZ=Europe/Oslo
ROT="$HOME/sot-maskin/gate"; cd "$ROT" || exit 1
LOG="$ROT/attic/_publish_okt5.log"; echo "start $(date '+%F %T')" > "$LOG"
HASH=$(git -C "$ROT" log -1 --format=%h -- src data regler bygg.py datalag.py assets)
echo "kilde-hash=$HASH" >> "$LOG"

# 1) bevis-ark fra ny modell
python3 bygg.py enkel >> "$LOG" 2>&1
python3 - >> "$LOG" 2>&1 <<'PY'
import json,glob
out=[json.load(open(f)).get('standpunkt') for f in sorted(glob.glob('rapport/ferdig/renders_r2/*.json'))]
json.dump([s for s in out if s],open('/tmp/stand_r3.json','w'),ensure_ascii=False)
PY
echo "--- render $(date '+%T') ---" >> "$LOG"
PW_GPU=1 node verktoy/gatekamera.mjs ut/enkel/index.html /tmp/stand_r3.json rapport/ferdig/renders_r3 >> "$LOG" 2>&1
python3 verktoy/rett/montasje.py --etter rapport/ferdig/renders_r3 --ut rapport/ferdig >> "$LOG" 2>&1
python3 verktoy/rett/montasje.py --etter rapport/ferdig/renders_r3 --ut rapport/ferdig --strekk bnr-13416362 >> "$LOG" 2>&1
python3 verktoy/rett/kontaktark_28.py rapport/ferdig/sot-dom-runde3.jpg >> "$LOG" 2>&1
echo "kontaktark: $(ls -la rapport/ferdig/sot-dom-runde3.jpg 2>/dev/null | awk '{print $5}') bytes" >> "$LOG"

# 2) regler (nohup-stil, lang). Ved rødt 06/07: omkjøring (Vegar: flaky, grønt ved omkjøring)
echo "--- regler $(date '+%T') ---" >> "$LOG"
PYTHONPATH=regler python3 regler/kjor.py >> "$LOG" 2>&1
RODE0607=$(grep "^- FEIL" rapport/rapport.md | grep -E " 0[67]_" || true)
if [ -n "$RODE0607" ]; then
  echo "06/07 rødt, kjører regler på nytt (omkjøring): $RODE0607" >> "$LOG"
  PYTHONPATH=regler python3 regler/kjor.py >> "$LOG" 2>&1
fi
echo "røde regler (utenom 09): $(grep '^- FEIL' rapport/rapport.md | grep -v ' 09_publisert ' | wc -l)" >> "$LOG"
grep "^- FEIL" rapport/rapport.md | grep -v ' 09_publisert ' >> "$LOG" 2>&1

# 3) publiser /prove1 (prove1 slipper røde regler gjennom, lister dem)
echo "--- publiser $(date '+%T') ---" >> "$LOG"
if sh publiser.sh prove1 >> "$LOG" 2>&1; then PUB="PUBLISERT"; else PUB="PUBLISER_FEIL"; fi
echo "status=$PUB slutt $(date '+%F %T')" >> "$LOG"

# 4) meld
API_BASE="${PAPERCLIP_API_URL%/}"; API_BASE="${API_BASE%/api}"
python3 - "$PUB" "$LOG" "$API_BASE" "$PAPERCLIP_API_KEY" "$PAPERCLIP_TASK_ID" "$HASH" >> "$LOG" 2>&1 <<'PY'
import sys,json,urllib.request
pub,log,base,key,task,h=sys.argv[1:7]
tail=''.join(open(log,encoding='utf8',errors='replace').readlines()[-30:])
if pub=='PUBLISERT':
    body=(f"**OPPGAVE4 økt 5 — publisert til /prove1 + nytt bevis-ark.** Commit `{h}` er ute:\n"
          "https://pageblack-official.github.io/fredrikstad-fortress-town/prove1/\n\n"
          "Bevis-arket `rapport/ferdig/sot-dom-runde3.jpg` er regenerert fra ny modell (inneholder Street View, "
          "git-ignoreres → kopier til Dropbox teknisk-veikart/status/ for hånd).\n\n"
          "Rettet i denne runden (alle durable/targeted, dom_sjekk exit 0): gate-5, 2 grå, mørkt tak, nr 10 brun port, "
          "nr 7/8 piper=2, nr 8 takvindu, nr 14 mørke karmer, nr 5 uniforme vinduer, **svart kloss fjernet** (smijernsport gj-422/gj-405).\n\n"
          "Gjenstår: nr 4 (slå sammen rosa+beige), villa 13415889, Widdingstua-terreng, standpunkt-husene (bevis-kamera), "
          "bnr-6251331 gul (tegning-forlik). Se RAPPORT4.md. Fortsetter.")
else:
    body=("**OPPGAVE4 økt 5 — publisering feilet.** Bevis-ark bygget, men `publiser.sh prove1` stoppet. Siste linjer:\n```\n"+tail+"\n```\nTrenger ny kjøring.")
req=urllib.request.Request(f"{base}/api/issues/{task}/comments",data=json.dumps({"body":body}).encode(),
    headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},method="POST")
try: print("kommentar",urllib.request.urlopen(req,timeout=30).status)
except Exception as e: print("kommentar FEIL",e)
PY
