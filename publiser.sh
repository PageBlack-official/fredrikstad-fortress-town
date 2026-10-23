#!/bin/sh
# Legger server-bygget (ut/server) på grenen gh-pages, som GitHub Pages serverer. Bruk: sh publiser.sh
set -e
ROT=$(cd "$(dirname "$0")" && pwd)
python3 "$ROT/bygg.py" server
TMP=$(mktemp -d)
git -C "$ROT" worktree add --detach "$TMP" >/dev/null 2>&1 || true
cd "$TMP"
git checkout --orphan gh-pages >/dev/null 2>&1
git rm -rfq . >/dev/null 2>&1 || true
cp -R "$ROT/ut/server/." .
touch .nojekyll
git add -A
git commit -qm "Pages: versjon $(cat "$ROT/VERSJON") $(date +%Y-%m-%d)"
git push -f origin gh-pages
cd "$ROT"; git worktree remove --force "$TMP"
echo "publisert gh-pages, versjon $(cat "$ROT/VERSJON")"
