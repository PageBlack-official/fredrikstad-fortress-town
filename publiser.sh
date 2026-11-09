#!/bin/sh
# Legger kartet ut på GitHub Pages (grenen gh-pages). To veier, og ingen av dem kan bytte feil adresse:
#   sh publiser.sh prove     -> bare /prove/ byttes (ett-fils-bygget). Forsiden og /backup/ står som de står på gh-pages.
#   sh publiser.sh prove1    -> bare /prove1/ byttes (07.11, Vegar: nattens «the basics» på egen adresse ved siden av /prove/)
#   sh publiser.sh forside   -> forsiden byttes (server-bygget) og /prove/ får samme bygg. Den gamle forsiden flyttes til
#                               /backup/v<versjon>-<dato>/ og føres i lista. Krever Vegars ja og en grønn maskinsjekk (rapport/maskin.json)
#                               fra hans Chrome mot akkurat denne kilden (verktoy/maskin-sjekk.js, LESMEG «Maskinsjekken»).
# (Før 05.11 bygde «prove» også forsiden på nytt fra SERVER_FRA; det la nye bygg på forsiden uten ja og mistet backupene.)
set -e
export TZ=Europe/Oslo
ROT=$(cd "$(dirname "$0")" && pwd)
MODUS="$1"
if [ "$MODUS" != "prove" ] && [ "$MODUS" != "prove1" ] && [ "$MODUS" != "forside" ]; then echo "bruk: sh publiser.sh prove | prove1 | forside"; exit 1; fi
PROVE=prove; [ "$MODUS" = "prove1" ] && PROVE=prove1
# Sperre: ingen publisering uten fersk samlerapport kjørt mot akkurat denne kilden (regler/kjor.py). På /prove/ slipper røde regler
# gjennom, men listes; forsiden stopper på røde regler utenom 09 (publisert versjon er alltid gammel rett før en ny publisering).
HASH=$(git -C "$ROT" log -1 --format=%h -- src data regler bygg.py datalag.py assets); URETTET=$(git -C "$ROT" status --porcelain -- src data regler bygg.py datalag.py assets)
RAPP="$ROT/rapport/rapport.md"; VERSJON=$(cat "$ROT/VERSJON")
if [ -n "$URETTET" ]; then echo "STOPP: urettede endringer i kilden; commit først, så regler/kjor.py"; exit 1; fi
if ! grep -q "^Kilde: $HASH versjon $VERSJON " "$RAPP" 2>/dev/null; then echo "STOPP: rapport/rapport.md er ikke kjørt mot $HASH (kjør: PYTHONPATH=regler python3 regler/kjor.py)"; exit 1; fi
# Regel 48 (PAG-1496): vinduer som ligger oppå hverandre (over 5 % overlapp i bygg[].vind) stopper ALL publisering,
# også /prove og /prove1 der andre røde regler ellers slipper gjennom. Rød = stopp, uansett modus.
if grep -q "^- FEIL 48_" "$RAPP"; then echo "STOPP: regel 48 er rød — vinduer ligger oppå hverandre (PAG-1496):"; grep "^- FEIL 48_" "$RAPP"; exit 1; fi
RODE=$(grep "^- FEIL" "$RAPP" | grep -v " 09_publisert " || true)
if [ -n "$RODE" ]; then
  if [ "$MODUS" != "forside" ] || [ -n "$TILLAT_RODE" ]; then echo "røde regler går ut (${TILLAT_RODE:-prove}):"; echo "$RODE"; else echo "STOPP: røde regler (TILLAT_RODE='<Vegars ja>' når han har bestemt det):"; echo "$RODE"; exit 1; fi
fi
if [ "$MODUS" = "forside" ]; then
  python3 - "$ROT/rapport/maskin.json" "$HASH" <<'PY' || exit 1
import json, sys
try: m = json.load(open(sys.argv[1]))
except Exception: sys.exit('STOPP: rapport/maskin.json mangler (maskinsjekken i Vegars Chrome, LESMEG «Maskinsjekken»)')
if m.get('kilde') != sys.argv[2]: sys.exit(f"STOPP: maskinsjekken er kjørt mot {m.get('kilde')}, ikke {sys.argv[2]} (legg ut på /prove/ og kjør den der)")
if not m.get('ok'): sys.exit('STOPP: maskinsjekken er rød: ' + '; '.join(m.get('feil', [])))
print('maskinsjekk grønn:', m.get('gpu'), m.get('ms_per_bilde'), 'ms per bilde')
PY
fi
python3 "$ROT/bygg.py" enkel >/dev/null; [ "$MODUS" = "forside" ] && python3 "$ROT/bygg.py" server >/dev/null
git -C "$ROT" fetch -q origin gh-pages
TMP=$(mktemp -d); GREN="pages-$(date +%s)"
git -C "$ROT" worktree add --detach "$TMP" >/dev/null
cd "$TMP"
# (08.11) vanlig commit oppå det som ligger ute, ikke en foreldreløs gren: da holder en vanlig push (ingen force), og historikken står
git checkout -q -b "$GREN" origin/gh-pages
mkdir -p "$PROVE"; cp "$ROT/ut/enkel/index.html" "$PROVE/index.html"
if [ "$MODUS" = "forside" ]; then
  B="backup/v$VERSJON-$(date +%d%b | tr 'A-Z' 'a-z')"; [ -e "$B" ] && B="$B-$(date +%H%M)"; mkdir -p "$B"
  for f in $(ls -A | grep -v -x -e prove -e backup -e .nojekyll -e .git); do mv "$f" "$B/"; done
  python3 - "$TMP/backup/index.html" "$(basename "$B")" "$(date '+%d.%m.%Y kl. %H.%M')" <<'PY'
import sys
p, mappe, naar = sys.argv[1:]
s = open(p, encoding='utf8').read()
s = s.replace('<ul>\n', f'<ul>\n<li><a href="{mappe}/">Forsiden fram til {naar}</a></li>\n', 1)
open(p, 'w', encoding='utf8').write(s)
PY
  cp -R "$ROT/ut/server/." .
fi
touch .nojekyll
git add -A
git commit -qm "Pages ($MODUS): versjon $VERSJON, kilde $HASH, $(date +%Y-%m-%d)"
# (08.11) minien pusher selv med egen deploy-nøkkel (~/.ssh/sot_deploy, remote «pages» = git@github-sot:…); uten den: origin
PUSH=origin; git -C "$ROT" remote get-url pages >/dev/null 2>&1 && PUSH=pages
git push "$PUSH" "$GREN:gh-pages"
cd "$ROT"; git worktree remove --force "$TMP"; git branch -q -D "$GREN"
git branch -q -D gh-pages 2>/dev/null || true
# venter til /prove/ viser den nye kilden (23.10: publiseringen stoppet stille og Pages stod på en gammel versjon hele kvelden)
URL="https://pageblack-official.github.io/fredrikstad-fortress-town/$PROVE/"
for i in $(seq 1 40); do
  curl -s -A sot-publiser "$URL?n=$i$$" | grep -q "name=\"kilde\" content=\"$HASH\"" && { echo "publisert gh-pages ($MODUS), versjon $VERSJON, kilde $HASH (sjekket ute etter $((i * 15)) s)"; exit 0; }
  sleep 15
done
echo "STOPP: pushet til gh-pages, men /$PROVE/ viser ikke kilde $HASH etter 10 min (sjekk GitHub Pages)"; exit 1
