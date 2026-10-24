#!/bin/sh
# Kontaktark: tre faste utsnitt (Torvet, kvartal 2, hjemmevisning) av et bygg, uten UI. Bruk: sh kontaktark.sh <index.html> <utprefiks>
set -e
H=$(cd "$(dirname "$0")" && pwd)
UI=0 node "$H/bilde.mjs" "$1" "$2-torvet.png" 40 3 15 42 1100 750 >/dev/null
UI=0 node "$H/bilde.mjs" "$1" "$2-kvartal2.png" 40 2.5 19 72 1100 750 >/dev/null
UI=0 node "$H/bilde.mjs" "$1" "$2-hjem.png" >/dev/null
echo "kontaktark $2-{torvet,kvartal2,hjem}.png"
