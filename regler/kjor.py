"""Kjører alle reglene og samler rapport/rapport.md. Ingen publisering uten at alt som kan være grønt, er grønt.
Rapporten merkes med kilden den er kjørt mot (git-hash, om noe var urettet, versjon), så publiser.sh kan nekte å publisere
på en gammel rapport (28.10: samlerapporten stod på v32 mens /prove/ fikk v33 og Kaserna)."""
import subprocess, sys, os, glob, datetime
ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def git(*a): return subprocess.run(['git', '-C', ROT, *a], capture_output=True, text=True).stdout.strip()
ut = []
for f in sorted(glob.glob(os.path.join(ROT, 'regler', '[0-9]*.py'))):
    r = subprocess.run([sys.executable, f], capture_output=True, text=True, cwd=os.path.join(ROT, 'regler'), env={**os.environ, 'PYTHONPATH': os.path.join(ROT, 'regler')})
    ut.append(r.stdout.strip() or ('FEIL ' + os.path.basename(f) + ' krasjet: ' + r.stderr.strip()[-300:]))
hash_ = git('rev-parse', '--short', 'HEAD'); urettet = git('status', '--porcelain', '--', 'src', 'data', 'regler', 'bygg.py', 'datalag.py', 'assets')
versjon = open(os.path.join(ROT, 'VERSJON')).read().strip()
hode = f"Kilde: {hash_}{'+urettet' if urettet else ''} versjon {versjon} kjørt {datetime.datetime.now():%Y-%m-%d %H:%M}"
open(os.path.join(ROT, 'rapport', 'rapport.md'), 'w', encoding='utf8').write('# Regelrapport\n\n' + hode + '\n\n' + '\n'.join('- ' + u for u in ut) + '\n\nDetaljer per regel i samme mappe.\n')
print(hode); print('\n'.join(ut))
