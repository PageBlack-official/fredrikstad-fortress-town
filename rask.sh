#!/bin/sh
# rask.sh — Hurtigsporet (PAG-1504, Vegar 10.11: «Hurtigspor først»). Legger kildens NÅVÆRENDE committede tilstand
# ut på https://pageblack-official.github.io/fredrikstad-fortress-town/rask/ på ≤ 10 min fra commit, uten full regelkjøring.
#
#   sh rask.sh
#
# Hva det IKKE gjør (harde grenser):
#   * Rører ALDRI /prove, /prove1, /backup eller forsiden. Bare mappa rask/ på gh-pages byttes.
#   * Force-pusher ALDRI. Ved avvist push hentes gh-pages på nytt og rask/ legges oppå igjen (til 5 forsøk).
#   * Kjører IKKE de ~45 reglene. Bare de raske vaktreglene som stopper et ødelagt kart (se under).
#     Full regelkjøring + maskinsjekk hører til /prove og forsiden (publiser.sh), ikke hit.
#
# Flyten (dokumentert i rapport/rask/RAPPORT.md og skillen): Vegar dømmer hus -> agent retter i kilden -> commit -> sh rask.sh
#   -> lenke rask/?hus=<bnr> til huset i saken.
set -e
export TZ=Europe/Oslo
export PATH="$HOME/sot-maskin/py/bin:$HOME/sot-maskin/node/bin:$PATH"
export PW_GPU=1                      # Mac-ens eget skjermkort: last-testen går på sekunder, ikke minutter
ROT=$(cd "$(dirname "$0")" && pwd)
cd "$ROT"
T0=$(date +%s)

# Worktreet deler repoets node_modules (gitignorert, så lenka må finnes her slik den gjør i gate/)
[ -e node_modules ] || ln -sfn "$HOME/sot-maskin/repo/node_modules" node_modules

# --- 0) kilden må være committet. Hjørnestemplet viser kilde-commit; urettede endringer ville gjort det til en løgn. ---
URETTET=$(git -C "$ROT" status --porcelain -- src data regler bygg.py datalag.py assets)
if [ -n "$URETTET" ]; then
  echo "STOPP: urettede endringer i kilden — commit først (hurtigsporet viser kilde-commit i hjørnet):"
  echo "$URETTET"; exit 1
fi
HASH=$(git -C "$ROT" log -1 --format=%h -- src data regler bygg.py datalag.py assets)
HASHFULL=$(git -C "$ROT" log -1 --format=%H -- src data regler bygg.py datalag.py assets)
CMT_EPOCH=$(git -C "$ROT" log -1 --format=%ct "$HASHFULL")
NAAR=$(date '+%d.%m.%Y kl. %H.%M')
VERSJON=$(cat "$ROT/VERSJON")

# --- 1) hvilke hus endret seg (git diff mot forrige /rask-bygg). Artefaktet er ett samlet bygg (enkel), så selve HTML-en ---
#         kan ikke bygges per hus; diffen brukes til lenka og rapporten, og til å si fra når ingenting i kilden er rørt.
SIST=$(cat "$ROT/rapport/rask-sist.txt" 2>/dev/null || true)
ENDRET=$(python3 - "$ROT" "$SIST" "$HASHFULL" <<'PY'
import json, subprocess, sys
rot, sist, naa = sys.argv[1], sys.argv[2], sys.argv[3]
def git(*a): return subprocess.run(['git','-C',rot,*a], capture_output=True, text=True).stdout
def bygg_ved(ref):
    try: return {b['id']: json.dumps(b, sort_keys=True) for b in json.loads(git('show', f'{ref}:data/bygg.json'))}
    except Exception: return None
if not sist:
    print('FORSTE'); sys.exit()                    # ingen forrige: hele byen
endret_filer = git('diff','--name-only', f'{sist}..{naa}').split()
if not endret_filer:
    print('INGEN'); sys.exit()                      # kilden urørt siden forrige /rask
a, b = bygg_ved(sist), bygg_ved(naa)
hus = []
if a is not None and b is not None:
    hus = sorted({k[4:] for k in set(a)|set(b) if a.get(k) != b.get(k)})   # bnr uten "bnr-"
# bare bygg.json-diff gir presise hus; endres src/datalag/assets rammer det alle, så da lar vi hus-lista stå tom
print('HUS ' + ' '.join(hus) if hus else 'ANNET ' + ' '.join(endret_filer[:8]))
PY
)
case "$ENDRET" in
  FORSTE) echo "første /rask-bygg (ingen forrige å diffe mot) — bygger hele byen" ;;
  INGEN)  echo "kilden er urørt siden forrige /rask (kilde $HASH) — bygger og publiserer på nytt likevel (nytt tidsstempel i hjørnet)" ;;
  HUS\ *) echo "endrede hus (git diff $SIST..$HASH): $(echo "$ENDRET" | cut -d' ' -f2-)" ;;
  ANNET\ *) echo "endringer utenfor enkelthus (src/datalag/assets): $(echo "$ENDRET" | cut -d' ' -f2-)" ;;
esac
HUS1=$(echo "$ENDRET" | awk '/^HUS/{print $2}')     # første endrede bnr, til lenke-eksemplet

# --- 2) bygg (enkel). Ett samlet artefakt; ~3–4 s, godt innenfor budsjettet. ---
echo "bygger (enkel) fra kilde $HASH ..."
TB0=$(date +%s); python3 bygg.py enkel >/dev/null; TB1=$(date +%s)
echo "  bygd på $((TB1-TB0)) s"

# --- 3) raske vaktregler: bare det som stopper et ødelagt kart. Resten kjøres som før for /prove1 og /prove. ---
#   a) bygger og laster + ingen JS-feil  (verktoy/last-test.mjs: hodeløs Chromium, window.__vis finnes, feil-lista tom)
#   b) 48 vinduer ikke oppå hverandre    (regler/48 — ren Python, rask; samme regel som sperrer publiser.sh)
echo "vakt a) bygger og laster, ingen JS-feil ..."
LAST=$(node verktoy/last-test.mjs ut/enkel/index.html 2>&1 | tail -1); echo "  $LAST"
case "$LAST" in
  *"lastet: true"*"feil: []"*) : ;;
  *) echo "STOPP: kartet lastet ikke rent (bygger og laster / ingen JS-feil). Ikke publisert til /rask."; exit 1 ;;
esac
echo "vakt b) 48 vinduer ikke oppå hverandre ..."
if ! PYTHONPATH=regler python3 regler/48_vinduer_ikke_oppaa_hverandre.py; then
  echo "STOPP: regel 48 rød — vinduer ligger oppå hverandre. Ikke publisert til /rask."; exit 1
fi

# --- 4) pynt rask-kopien: hjørnestempel (kilde-commit + tidspunkt) og ?hus=<bnr>-sjia. Rører ikke src/ eller /prove-bygget. ---
RASKHTML=$(mktemp)
python3 - ut/enkel/index.html "$RASKHTML" "$HASH" "$NAAR" "$VERSJON" <<'PY'
import sys
inn, ut, hash_, naar, versjon = sys.argv[1:6]
s = open(inn, encoding='utf8').read()
# ?hus=<bnr> -> #hus=bnr-<bnr> FØR modulen evalueres (klassisk inline-skript kjører før deferred module).
# Den eksisterende delings-lenka (#hus=<bygg-id>, 15_lenke.js) løfter huset og glir kameraet dit; vi gjenbruker den.
shim = ("<script>(function(){try{var q=new URLSearchParams(location.search);var h=q.get('hus');"
        "if(h){h=h.trim();if(!/^[a-z]+-/i.test(h))h='bnr-'+h;"
        "if(!/(^|[#&])hus=/.test(location.hash))location.hash=(location.hash?location.hash.replace(/^#/,'')+'&':'')+'hus='+h;}}"
        "catch(e){}})();</script>")
# hjørnestempel: Vegar ser med én gang at det er den nye kilden
merke = (f'<div id="raskmerke">rask · kilde {hash_} · v{versjon} · {naar}</div>'
         '<style>#raskmerke{position:fixed;right:8px;bottom:8px;z-index:9999;'
         'font:11px/1.4 ui-monospace,Menlo,monospace;color:#3a2c26;background:rgba(226,225,214,.82);'
         'padding:3px 8px;border-radius:5px;pointer-events:none;letter-spacing:.2px}</style>')
s = s.replace('</head>', shim + '\n</head>', 1)
s = s.replace('</body>', merke + '\n</body>', 1)
open(ut, 'w', encoding='utf8').write(s)
PY

# --- 5) publiser bare rask/ til gh-pages. Vanlig commit oppå det som ligger ute (ingen force); ved avvisning: hent og prøv igjen. ---
git -C "$ROT" fetch -q origin gh-pages
TMP=$(mktemp -d); GREN="pages-rask-$(date +%s)"
git -C "$ROT" worktree add --detach "$TMP" >/dev/null
cd "$TMP"
PUSH=origin; git -C "$ROT" remote get-url pages >/dev/null 2>&1 && PUSH=pages
FORSOK=1
while :; do
  git checkout -q -B "$GREN" origin/gh-pages
  mkdir -p rask; cp "$RASKHTML" rask/index.html; touch .nojekyll
  git add -A rask .nojekyll
  git commit -qm "rask (hurtigspor): kilde $HASH, versjon $VERSJON, $(date +%Y-%m-%d) [PAG-1504]"
  if git push "$PUSH" "$GREN:gh-pages" 2>/tmp/raskpush.$$; then break; fi
  if [ "$FORSOK" -ge 5 ]; then
    echo "STOPP: klarte ikke pushe rask/ til gh-pages uten force etter 5 forsøk:"; cat /tmp/raskpush.$$
    cd "$ROT"; git worktree remove --force "$TMP"; git branch -q -D "$GREN" 2>/dev/null || true; exit 1
  fi
  echo "push avvist (noen andre publiserte imens) — henter gh-pages på nytt (forsøk $FORSOK)"
  git -C "$ROT" fetch -q origin gh-pages; FORSOK=$((FORSOK+1))
done
rm -f /tmp/raskpush.$$
cd "$ROT"; git worktree remove --force "$TMP"; git branch -q -D "$GREN" 2>/dev/null || true
git branch -q -D gh-pages 2>/dev/null || true

# --- 6) vent til /rask/ viser den nye kilden, så mål commit -> synlig ---
URL="https://pageblack-official.github.io/fredrikstad-fortress-town/rask/"
for i in $(seq 1 40); do
  if curl -s -A sot-rask "$URL?n=$i$$" | grep -q "name=\"kilde\" content=\"$HASH\""; then
    T1=$(date +%s)
    echo "$HASHFULL" > "$ROT/rapport/rask-sist.txt"
    echo "publisert /rask/, kilde $HASH, versjon $VERSJON"
    echo "  commit -> synlig: $((T1-CMT_EPOCH)) s   (rask.sh-start -> synlig: $((T1-T0)) s)"
    [ -n "$HUS1" ] && echo "  lenke til endret hus: ${URL}?hus=${HUS1}"
    echo "  lenkeform per hus: ${URL}?hus=<bnr>   (bnr = bygningsnummer, f.eks. 193870325 = Hovedvakten)"
    exit 0
  fi
  sleep 15
done
echo "STOPP: pushet til gh-pages, men /rask/ viser ikke kilde $HASH etter 10 min (sjekk GitHub Pages)"; exit 1
