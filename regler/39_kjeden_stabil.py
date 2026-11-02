"""Regel (02.11, avvik A5): kjeden gir det som ligger i repoet. Ingen rettelse lever bare fordi kjeden ikke er kjørt siden.
Vegar 02.11 16:44: «Jeg ser at vi har litt versjonskonflikt fremdeles.»
Årsaken til A1/A2: rettelser som var lagt inn utenfor kjeden (verktoy/kaserna.py 27.10, pb-51 sin murfarge for hånd 30.10) ble
overstyrt neste gang et verktøy i kjeden gikk (fasade_tegning.py 29.10, vegg_nye.py 30.10), eller ble liggende med gamle mål
(gårdsmurene fra før grunnmuren). Regelen kopierer repoet til en midlertidig mappe, kjører verktoy/bygg_kjede.py der (uten grunnmur,
ca. 4 minutter) og sammenligner dataene slik kartet ser dem (datalag.alle). Rød når et felt på et objekt blir annerledes;
tekstfelt som bare forklarer kilden (*_kilde) teller ikke (IoU-tall i teksten kan flytte seg i andre desimal).
"""
import sys, json, shutil, subprocess, tempfile
from _felles import *

UT = ('.git', 'node_modules', 'ut', '__pycache__')
KODE = "import sys,json;sys.path.insert(0,'.');import datalag;print(json.dumps(datalag.alle()))"


def eff(rot):
    r = subprocess.run([sys.executable, '-c', KODE], cwd=rot, capture_output=True, text=True)
    return json.loads(r.stdout)


tmp = tempfile.mkdtemp(prefix='kjede-')
try:
    kopi = os.path.join(tmp, 'repo')
    shutil.copytree(ROT, kopi, ignore=shutil.ignore_patterns(*UT), symlinks=True)
    r = subprocess.run([sys.executable, 'verktoy/bygg_kjede.py'], cwd=kopi, capture_output=True, text=True)
    if r.returncode:
        rapport('39_kjeden_stabil', False, ['kjeden feilet i kopien', r.stdout[-800:], r.stderr[-800:]]); sys.exit()
    a, b = eff(ROT), eff(kopi)
    feil = []
    for emne in sorted(set(a) | set(b)):
        A, B_ = a.get(emne), b.get(emne)
        if json.dumps(A, sort_keys=True) == json.dumps(B_, sort_keys=True): continue
        if isinstance(A, list) and isinstance(B_, list) and all(isinstance(x, dict) and 'id' in x for x in A + B_):
            ia = {x['id']: x for x in A}; ib = {x['id']: x for x in B_}
            for i in sorted(set(ia) | set(ib)):
                x, y = ia.get(i, {}), ib.get(i, {})
                ulike = [k for k in sorted(set(x) | set(y)) if not k.endswith('_kilde')
                         and json.dumps(x.get(k), sort_keys=True) != json.dumps(y.get(k), sort_keys=True)]
                if ulike: feil.append(f"FEIL {emne} {i}: {', '.join(ulike)} blir annerledes når kjeden kjøres")
        else:
            feil.append(f"FEIL {emne}: blir annerledes når kjeden kjøres")
    rapport('39_kjeden_stabil', not feil, [f"{len(feil)} objekter endres av en ny kjøring av kjeden"] + feil[:200]
            + [''] + [l for l in r.stdout.splitlines()])
finally:
    shutil.rmtree(tmp, ignore_errors=True)
