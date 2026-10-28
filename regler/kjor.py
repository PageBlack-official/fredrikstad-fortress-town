"""Kjører reglene og samler rapport/rapport.md fra rapport/<regel>.md. Ingen publisering uten at alt som kan være grønt, er grønt.
Bruk: python3 regler/kjor.py            alle reglene
      python3 regler/kjor.py 08 15 16   bare disse; sammendraget bygges likevel fra alle regel-filene
Rapporten merkes med kilden den er kjørt mot (git-hash, om noe var urettet, versjon), så publiser.sh kan nekte å publisere
på en gammel rapport (28.10: samlerapporten stod på v32 mens /prove/ fikk v33 og Kaserna)."""
import subprocess, sys, os, glob, datetime, re
ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def git(*a): return subprocess.run(['git', '-C', ROT, *a], capture_output=True, text=True).stdout.strip()
valgte = sys.argv[1:]
for f in sorted(glob.glob(os.path.join(ROT, 'regler', '[0-9]*.py'))):
    navn = os.path.basename(f)[:-3]
    if valgte and navn[:2] not in valgte: continue
    r = subprocess.run([sys.executable, f], capture_output=True, text=True, cwd=os.path.join(ROT, 'regler'), env={**os.environ, 'PYTHONPATH': os.path.join(ROT, 'regler')})
    if not r.stdout.strip():   # krasjet: skriv en rød regel-fil, så sammendraget viser det
        open(os.path.join(ROT, 'rapport', navn + '.md'), 'w', encoding='utf8').write(f"# {navn}: FEIL\n\nkrasjet: {r.stderr.strip()[-300:]}\n")
    print(r.stdout.strip() or f'FEIL {navn} krasjet')
ut = []
for f in sorted(glob.glob(os.path.join(ROT, 'regler', '[0-9]*.py'))):
    navn = os.path.basename(f)[:-3]; p = os.path.join(ROT, 'rapport', navn + '.md')
    if not os.path.exists(p): ut.append(f'FEIL {navn}  (ikke kjørt)'); continue
    linjer = [l.rstrip('\n') for l in open(p, encoding='utf8')]
    m = re.match(r'# (\S+): (OK|FEIL)', linjer[0]); forste = next((l for l in linjer[1:] if l.strip()), '')
    ut.append(f"{'OK  ' if m and m.group(2) == 'OK' else 'FEIL'} {navn}  ({forste.strip()[:160]})")
hash_ = git('log', '-1', '--format=%h', '--', 'src', 'data', 'regler', 'bygg.py', 'datalag.py', 'assets');   # siste commit som rørte kilden, så en rapport-commit ikke gjør rapporten gammel urettet = git('status', '--porcelain', '--', 'src', 'data', 'regler', 'bygg.py', 'datalag.py', 'assets')
versjon = open(os.path.join(ROT, 'VERSJON')).read().strip()
hode = f"Kilde: {hash_}{'+urettet' if urettet else ''} versjon {versjon} kjørt {datetime.datetime.now():%Y-%m-%d %H:%M}"
open(os.path.join(ROT, 'rapport', 'rapport.md'), 'w', encoding='utf8').write('# Regelrapport\n\n' + hode + '\n\n' + '\n'.join('- ' + u for u in ut) + '\n\nDetaljer per regel i samme mappe.\n')
print(hode)
