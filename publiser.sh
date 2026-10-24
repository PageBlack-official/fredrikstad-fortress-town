#!/bin/sh
# Legger server-bygget (ut/server) på grenen gh-pages, som GitHub Pages serverer. Bruk: sh publiser.sh
# Bygger en fersk, historieløs gren hver gang (midlertidig navn, så det går også når gh-pages finnes lokalt fra før).
set -e
ROT=$(cd "$(dirname "$0")" && pwd)
if [ -z "$SERVER_FRA" ]; then python3 "$ROT/bygg.py" server; else rm -rf "$ROT/ut/server"; cp -r "$SERVER_FRA" "$ROT/ut/server"; fi   # SERVER_FRA=<mappe>: legg ut et ferdig server-bygg (f.eks. forrige versjon) i stedet for å bygge
TMP=$(mktemp -d); GREN="pages-$(date +%s)"
git -C "$ROT" worktree add --detach "$TMP" >/dev/null
cd "$TMP"
git checkout -q --orphan "$GREN"
git rm -rfq . >/dev/null 2>&1 || true
cp -R "$ROT/ut/server/." .
# prøvebygg (valgfritt): sh publiser.sh prove legger ut/enkel/index.html (ett-fils-bygget) på /prove/ ved siden av det publiserte, til dom før det går inn
if [ "$1" = "prove" ]; then mkdir -p prove; cp "$ROT/ut/enkel/index.html" prove/index.html; fi
touch .nojekyll
git add -A
git commit -qm "Pages: versjon $(cat "$ROT/VERSJON") $(date +%Y-%m-%d)"
git push -f origin "$GREN:gh-pages"
cd "$ROT"; git worktree remove --force "$TMP"; git branch -q -D "$GREN"
git branch -q -D gh-pages 2>/dev/null || true
echo "publisert gh-pages, versjon $(cat "$ROT/VERSJON")"
