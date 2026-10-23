"""Kjører alle reglene og samler rapport/rapport.md. Ingen publisering uten at alt som kan være grønt, er grønt."""
import subprocess, sys, os, glob
ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ut = []
for f in sorted(glob.glob(os.path.join(ROT, 'regler', '[0-9]*.py'))):
    r = subprocess.run([sys.executable, f], capture_output=True, text=True, cwd=os.path.join(ROT, 'regler'), env={**os.environ, 'PYTHONPATH': os.path.join(ROT, 'regler')})
    ut.append(r.stdout.strip() or ('FEIL ' + os.path.basename(f) + ' krasjet: ' + r.stderr.strip()[-300:]))
open(os.path.join(ROT, 'rapport', 'rapport.md'), 'w', encoding='utf8').write('# Regelrapport\n\n' + '\n'.join('- ' + u for u in ut) + '\n\nDetaljer per regel i samme mappe.\n')
print('\n'.join(ut))
