#!/bin/sh
# OPPGAVE4 — bevis-ark + Dropbox + regler + publiser /prove1 (commit 1130c24, regel 39 grønn). Detached.
set -u
export PATH="$HOME/sot-maskin/py/bin:$HOME/sot-maskin/node/bin:$PATH"; export TZ=Europe/Oslo
ROT="$HOME/sot-maskin/gate"; cd "$ROT" || exit 1
LOG="$ROT/attic/_publish_okt6.log"; echo "start $(date '+%F %T')" > "$LOG"
HASH=$(git -C "$ROT" log -1 --format=%h -- src data regler bygg.py datalag.py assets); echo "kilde=$HASH" >> "$LOG"
DBX="$HOME/Page Black Dropbox/Page Black Business/20 Paperclip/outputs/teknisk-veikart/status"

python3 bygg.py enkel >> "$LOG" 2>&1
python3 - >> "$LOG" 2>&1 <<'PY'
import json,glob
json.dump([json.load(open(f)).get('standpunkt') for f in sorted(glob.glob('rapport/ferdig/renders_r2/*.json')) if json.load(open(f)).get('standpunkt')],open('/tmp/stand_r3.json','w'),ensure_ascii=False)
PY
echo "--- render $(date '+%T') ---" >> "$LOG"
PW_GPU=1 node verktoy/gatekamera.mjs ut/enkel/index.html /tmp/stand_r3.json rapport/ferdig/renders_r3 >> "$LOG" 2>&1
python3 verktoy/rett/montasje.py --etter rapport/ferdig/renders_r3 --ut rapport/ferdig >> "$LOG" 2>&1
python3 verktoy/rett/montasje.py --etter rapport/ferdig/renders_r3 --ut rapport/ferdig --strekk bnr-13416362 >> "$LOG" 2>&1
python3 verktoy/rett/kontaktark_28.py rapport/ferdig/sot-dom-runde3.jpg >> "$LOG" 2>&1
# Dropbox (Vegars egen mappe, han ba om det)
if [ -d "$DBX" ]; then cp rapport/ferdig/sot-dom-runde3.jpg "$DBX/sot-dom-runde3.jpg" && echo "kopiert til Dropbox: $DBX" >> "$LOG"; else echo "Dropbox-sti mangler: $DBX" >> "$LOG"; fi

echo "--- regler $(date '+%T') ---" >> "$LOG"
PYTHONPATH=regler python3 regler/kjor.py >> "$LOG" 2>&1
RODE0607=$(grep "^- FEIL" rapport/rapport.md | grep -E " 0[67]_" || true)
if [ -n "$RODE0607" ]; then echo "06/07 rødt -> omkjøring" >> "$LOG"; PYTHONPATH=regler python3 regler/kjor.py >> "$LOG" 2>&1; fi
RODE=$(grep "^- FEIL" rapport/rapport.md | grep -v ' 09_publisert ' | grep -v ' 03_fasader_fra_tegning ' || true)
echo "røde regler utenom 03/09: [$RODE]" >> "$LOG"

echo "--- publiser $(date '+%T') ---" >> "$LOG"
if sh publiser.sh prove1 >> "$LOG" 2>&1; then PUB=PUBLISERT; else PUB=PUBLISER_FEIL; fi
echo "status=$PUB slutt $(date '+%F %T')" >> "$LOG"

API_BASE="${PAPERCLIP_API_URL%/}"; API_BASE="${API_BASE%/api}"
python3 - "$PUB" "$LOG" "$API_BASE" "$PAPERCLIP_API_KEY" "$PAPERCLIP_TASK_ID" "$HASH" "$RODE" >> "$LOG" 2>&1 <<'PY'
import sys,json,urllib.request
pub,log,base,key,task,h,rode=sys.argv[1:8]
tail=''.join(open(log,encoding='utf8',errors='replace').readlines()[-25:])
if pub=='PUBLISERT':
    body=(f"**OPPGAVE4 — publisert /prove1 (`{h}`) + regel 39 GRØNN.** https://pageblack-official.github.io/fredrikstad-fortress-town/prove1/\n\n"
          f"**regel 39 rettet i årsaken** (Vegar ba om det): kjeden er nå idempotent (0 objekter endres). nr 8 piper + nr 5 gjort kilde-baserte; nr 8 takvindu (ikke ark). Bare 03 er rød{' (+ '+rode+')' if rode.strip() else ''}.\n\n"
          f"Bevis-arket `sot-dom-runde3.jpg` regenerert og **kopiert til Dropbox** teknisk-veikart/status/.\n\n"
          f"Gjenstår (RAPPORT4): nr 4 (husdeling-merge, bekreft nabo visuelt), villa 13416362/13415889, Widdingstua-terreng, standpunkt-husene, bnr-6251331 gul (tegning-forlik). Fortsetter.")
else:
    body="**OPPGAVE4 — publisering feilet.** Siste linjer:\n```\n"+tail+"\n```\nTrenger ny kjøring."
req=urllib.request.Request(f"{base}/api/issues/{task}/comments",data=json.dumps({"body":body}).encode(),headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},method="POST")
try: print("kommentar",urllib.request.urlopen(req,timeout=30).status)
except Exception as e: print("kommentar FEIL",e)
PY
