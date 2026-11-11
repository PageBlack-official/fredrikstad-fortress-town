#!/bin/sh
# OPPGAVE4 økt 3 — frittstående avslutter: venter til regelsuiten er ferdig mot commit 3876921,
# publiserer til /prove1, og melder utfallet som en Paperclip-kommentar. Kjøres detached (nohup) så
# den overlever at agent-økta rives ned. Rydder seg selv (logg + dette skriptet) via attic ikke nødvendig;
# filene ligger i rapport/ og committes aldri (bare mine eksplisitte add-er går i git).
set -u
export PATH="$HOME/sot-maskin/py/bin:$HOME/sot-maskin/node/bin:$PATH"
export TZ=Europe/Oslo
ROT="$HOME/sot-maskin/gate"
LOG="$ROT/rapport/_finish_okt3.log"
cd "$ROT" || exit 1
echo "start $(date '+%F %T')" > "$LOG"

# 1) vent på regelsuiten (maks ~40 min), til rapport.md tar commit 3876921 eller prosessen dør
i=0
while [ $i -lt 160 ]; do
  grep -q "^Kilde: 3876921 " rapport/rapport.md 2>/dev/null && break
  pgrep -f "regler/kjor.py" >/dev/null 2>&1 || break
  i=$((i+1)); sleep 15
done
KILDE_OK=$(grep -q "^Kilde: 3876921 " rapport/rapport.md 2>/dev/null && echo ja || echo nei)
echo "regler ferdig: kilde_3876921=$KILDE_OK (ventet $((i*15)) s)" >> "$LOG"

PUBOUT=""
STATUS=""
if [ "$KILDE_OK" = "ja" ]; then
  echo "--- publiser.sh prove1 ---" >> "$LOG"
  if sh publiser.sh prove1 >> "$LOG" 2>&1; then
    STATUS="PUBLISERT"
  else
    STATUS="PUBLISER_FEIL"
  fi
else
  STATUS="REGLER_UFERDIG"
fi
echo "status=$STATUS slutt $(date '+%F %T')" >> "$LOG"

# 2) meld utfallet som Paperclip-kommentar
API_BASE="${PAPERCLIP_API_URL%/}"; API_BASE="${API_BASE%/api}"
python3 - "$STATUS" "$LOG" "$API_BASE" "$PAPERCLIP_API_KEY" "$PAPERCLIP_TASK_ID" <<'PY'
import sys, json, urllib.request
status, logp, base, key, task = sys.argv[1:6]
tail = ''.join(open(logp, encoding='utf8', errors='replace').readlines()[-25:])
if status == 'PUBLISERT':
    body = ("**OPPGAVE4 økt 3 — publisert til /prove1.** Den nye versjonen (commit `3876921`, versjon 34) ligger nå ute:\n"
            "https://pageblack-official.github.io/fredrikstad-fortress-town/prove1/\n\n"
            "`dom_sjekk.py` exit 0 (Del B tellbare etter Vegars dom; Del A frosset). Regelsuiten kjørte grønt nok for /prove1 "
            "(røde regler slipper gjennom på prøveadressen og er listet i `rapport/rapport.md`; regel 03 er kjent rød).\n\n"
            "Gjenstår til neste kjøring: Del C (12 fargefiks/standpunkt), Del B ikke-tellbare og bevisbilder — se WORKLISTE i `rapport/ferdig/RAPPORT4.md`. "
            "Bare Vegar kan si «ferdig».")
elif status == 'PUBLISER_FEIL':
    body = ("**OPPGAVE4 økt 3 — publisering til /prove1 feilet.** Commit `3876921` er fersk og `dom_sjekk.py` gir exit 0, "
            "men `publiser.sh prove1` stoppet. Siste linjer:\n```\n" + tail + "\n```\nSaken trenger en ny kjøring for å fullføre publiseringen.")
else:
    body = ("**OPPGAVE4 økt 3 — regelsuiten ble ikke ferdig.** `regler/kjor.py` oppdaterte ikke `rapport/rapport.md` til kilde `3876921` "
            "før tidsavbrudd/stopp, så /prove1 er ikke publisert. Commit `3876921` og `dom_sjekk.py` exit 0 står. Siste linjer:\n```\n" + tail + "\n```\nSaken trenger en ny kjøring.")
req = urllib.request.Request(f"{base}/api/issues/{task}/comments",
    data=json.dumps({"body": body, "resume": True}).encode('utf8'),
    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}, method="POST")
try:
    r = urllib.request.urlopen(req, timeout=30)
    print("kommentar postet:", r.status, file=sys.stderr)
except Exception as e:
    print("kommentar FEIL:", e, file=sys.stderr)
PY
echo "kommentar-forsøk ferdig $(date '+%F %T')" >> "$LOG"
