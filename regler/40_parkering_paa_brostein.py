"""Regel (02.11, avvik A3): ingen glatt parkeringsflate oppå brosteinen. Der raden er målt som flate i ortofotoet
(flater[].parkering_id, verktoy/bakke.py parkeringsfelt), er flatens type det som tegnes, og bare oppmerkingen legges oppå.
Vegar 02.11 16:44: «Bygningsnummer 193972101 har fått et eller annet rart foran huset.» Det var parkeringsflaten til
parkering-1-4627 (Torvgaten, beboerparkering): src/17 tegnet kommunens rad som en glatt grå flate 12 cm over brosteinen, langs
hele garasjefasaden, i tillegg til den målte brosteinsflaten med oppmerking under.
Regelen regner ut hvilke parkeringsflater som tegnes (samme regel som src/17: målt flate går foran) og er rød når
  - src/17 ikke har regelen (parkeringsflaten tegnes uten å se etter flater[].parkering_id),
  - en parkeringsflate som tegnes, ligger med mer enn 20 % på brostein: en brosteinsflate i flater, eller brosteinsflaten når
    plassen ikke selv er målt som grus/asfalt i ortofotoet,
  - en parkeringsflate som tegnes, ligger med mer enn 10 % på gress eller i hus (avvik A6).
"""
import sys, glob
from _felles import *
sys.path.insert(0, ROT)
import datalag  # noqa: E402
from shapely.geometry import Polygon  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

d = datalag.alle()
feil, linjer = [], []
kode = open(glob.glob(os.path.join(ROT, 'src', '17_*.js'))[0], encoding='utf8').read()
if 'parkering_id' not in kode or 'maaltFlate' not in kode:
    feil.append('FEIL src/17 tegner parkeringsflaten uten å se etter målt flate (flater[].parkering_id)')
maalt = {f['parkering_id'] for f in d['flater'] if f.get('parkering_id') and not f.get('skjul')}
# brostein = flatene målt som brostein/heller; brosteinsflaten (landskap) teller bare der plassen selv ikke er målt som noe annet
# i ortofotoet (parkering[].flate, kilder/flater-maalt.json: grus eller asfalt er da det fotoet viser)
stein_flater = unary_union([Polygon(f['p']).buffer(0) for f in d['flater'] if not f.get('skjul') and f.get('typ') in ('brostein', 'heller') and len(f['p']) >= 3])
grunnstein = Polygon(d['brostein']).buffer(0)
tegnes = [p for p in d['parkering'] if p.get('p') and not p.get('skjul') and p['id'] not in maalt]
# gress og hus: en parkeringsflate som tegnes, skal ikke ligge over plen eller hus (A6 02.11: parkering-1-4625 lå over to hus og plenen)
gress = unary_union([Polygon(f['p']).buffer(0) for f in d['flater'] if not f.get('skjul') and f.get('typ') == 'gress' and len(f['p']) >= 3]
                    + [Polygon(g['p']).buffer(0) for g in d.get('gront', []) if not g.get('skjul') and len(g.get('p') or []) >= 3])
hus = unary_union([Polygon(b['p']).buffer(0) for b in d['bygg'] if not b.get('skjul') and len(b.get('p') or []) >= 3])
for p in tegnes:
    P = Polygon(p['p']).buffer(0)
    stein = stein_flater if p.get('flate') in ('grus', 'asfalt', 'gress') else stein_flater.union(grunnstein)
    andel = P.intersection(stein).area / max(P.area, 1e-6)
    g_ = P.intersection(gress).area / max(P.area, 1e-6); h_ = P.intersection(hus).area / max(P.area, 1e-6)
    galt = andel > 0.2 or g_ > 0.1 or h_ > 0.1
    (feil if galt else linjer).append(f"{'FEIL' if galt else 'ok  '} {p['id']} ({p.get('navn')}): parkeringsflaten tegnes, {andel:.0%} på brostein, {g_:.0%} på gress, {h_:.0%} i hus")
linjer.append(f"{len(maalt)} rader målt som flate (oppmerking på flaten, ingen parkeringsflate oppå)")
rapport('40_parkering_paa_brostein', not feil, [f"{len(feil)} feil; {len(tegnes)} parkeringsflater tegnes"] + feil + linjer)
