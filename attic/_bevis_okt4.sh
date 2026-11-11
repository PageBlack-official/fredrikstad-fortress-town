#!/bin/sh
# OPPGAVE4 økt 4 — frittstående bevis-sheet-bygger: rendrer alle 33 standpunkt fra den nye modellen,
# monterer SV | etter per hus, og stabler kontaktarket. Detached (nohup) så den overlever teardown.
set -u
export PATH="$HOME/sot-maskin/py/bin:$HOME/sot-maskin/node/bin:$PATH"
export TZ=Europe/Oslo
ROT="$HOME/sot-maskin/gate"; cd "$ROT" || exit 1
LOG="$ROT/attic/_bevis_okt4.log"; echo "start $(date '+%F %T')" > "$LOG"

# 1) fersk enkel-build (reflekterer alle committede rettelser)
python3 bygg.py enkel >> "$LOG" 2>&1

# 2) standpunkt-fil fra renders_r2/*.json (de 33 bevis-kameraene)
python3 - >> "$LOG" 2>&1 <<'PY'
import json,glob
out=[json.load(open(f)).get('standpunkt') for f in sorted(glob.glob('rapport/ferdig/renders_r2/*.json'))]
out=[s for s in out if s]
json.dump(out,open('/tmp/stand_r3.json','w'),ensure_ascii=False)
print(len(out),'standpunkter')
PY

# 3) render alle inn i renders_r3 (skjermkort)
echo "--- render $(date '+%T') ---" >> "$LOG"
PW_GPU=1 node verktoy/gatekamera.mjs ut/enkel/index.html /tmp/stand_r3.json rapport/ferdig/renders_r3 >> "$LOG" 2>&1
echo "render ferdig $(date '+%T'), $(ls rapport/ferdig/renders_r3/*.png 2>/dev/null | wc -l) png" >> "$LOG"

# 4) montasje SV | etter -> rapport/ferdig/<id>.jpg (utbrent 13416362 får --strekk separat)
python3 verktoy/rett/montasje.py --etter rapport/ferdig/renders_r3 --ut rapport/ferdig >> "$LOG" 2>&1
python3 verktoy/rett/montasje.py --etter rapport/ferdig/renders_r3 --ut rapport/ferdig --strekk bnr-13416362 >> "$LOG" 2>&1

# 5) kontaktark (SV | etter, 28 hus) -> sot-dom-runde3.jpg (INNEHOLDER SV, aldri git add)
python3 verktoy/rett/kontaktark_28.py rapport/ferdig/sot-dom-runde3.jpg >> "$LOG" 2>&1
echo "kontaktark: $(ls -la rapport/ferdig/sot-dom-runde3.jpg 2>/dev/null | awk '{print $5}') bytes" >> "$LOG"
echo "ferdig $(date '+%F %T')" >> "$LOG"

# 6) meld utfallet
API_BASE="${PAPERCLIP_API_URL%/}"; API_BASE="${API_BASE%/api}"
python3 - "$LOG" "$API_BASE" "$PAPERCLIP_API_KEY" "$PAPERCLIP_TASK_ID" >> "$LOG" 2>&1 <<'PY'
import sys,json,urllib.request
log,base,key,task=sys.argv[1:5]
tail=''.join(open(log,encoding='utf8',errors='replace').readlines()[-20:])
body=("**OPPGAVE4 økt 4 — bevis-ark regenerert fra den nye modellen.** Alle 33 standpunkt rendret på nytt, "
      "SV | etter montert per hus, kontaktark skrevet til `rapport/ferdig/sot-dom-runde3.jpg` (inneholder Street View, "
      "git-ignoreres; må kopieres til Dropbox `teknisk-veikart/status/sot-dom-runde3.jpg` for hånd/konnektor).\n\n"
      "Arket viser de rettede husene (gate-5, grå-fiks, mørkt tak, brun port). Resten av Del C/B-geometrien "
      "(nr 5/4/villa/terreng/standpunkt/svart kloss) står fortsatt — se RAPPORT4.md. Siste logglinjer:\n```\n"+tail+"\n```")
req=urllib.request.Request(f"{base}/api/issues/{task}/comments",data=json.dumps({"body":body}).encode(),
    headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},method="POST")
try: print("kommentar",urllib.request.urlopen(req,timeout=30).status)
except Exception as e: print("kommentar FEIL",e)
PY
