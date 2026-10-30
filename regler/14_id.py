"""Regel: hvert bygg har en fast id, og alt som peker på et bygg, peker på id-en.
- hvert bygg har id, og ingen id er brukt to ganger
- alle id-er som noen gang er delt ut (kilder/id-register.txt), finnes fortsatt (et bygg som skal bort, skjules med grunn)
- rettelser, porter og legende peker på id-er som finnes, aldri på plass i lista
- bygg med bnr-id har bygningsnummeret i matrikkelfeltet (nøkkelen og kilden sier det samme)
Se datalag.py for hvorfor bygningsnummeret i Matrikkelen er nøkkelen."""
from _felles import *
b = data('bygg', raa=True) + list({r['id']: r['verdi'] for r in data('rettelser') if r['op'] == 'ny' and r['emne'] == 'bygg'}.values())   # nye bygg fra rettelseslaget (op ny, 29.10)
feil = []
ids = [x.get('id') for x in b]
if None in ids: feil.append(f"- {ids.count(None)} bygg uten id")
dobbel = sorted({i for i in ids if i and ids.count(i) > 1})
if dobbel: feil.append(f"- id brukt flere ganger: {', '.join(dobbel)}")
reg = [l.strip() for l in open(os.path.join(ROT, 'kilder', 'id-register.txt'), encoding='utf8') if l.strip()]
# bakkeflatene har også faste id-er i samme register (27.10): gr- grøntflater, ga- gårdsrom, fl- flater målt i ortofotoet (verktoy/flater.py), vn- vannflater (verktoy/vann.py lag), br- brygger (verktoy/brygger.py maal)
flate_ids = []
for emne in ('gront', 'gardsrom', 'flater', 'vann', 'brygger', 'teglmurer', 'vinterhager', 'terrasser', 'gjerder'):   # gj- gjerder/murer/hekker (verktoy/bakke.py gjerder, 30.10)   # mu- gårdsmurer i tegl, vh- glasshus, te- verandaer (verktoy/kaserna.py, 27.10)
    try: fx = data(emne, raa=True)
    except FileNotFoundError: continue
    fi = [x.get('id') for x in fx if isinstance(x, dict)]
    if None in fi: feil.append(f"- {fi.count(None)} {emne} uten id (del ut med verktoy/flater.py id)")
    fd = sorted({i for i in fi if i and fi.count(i) > 1})
    if fd: feil.append(f"- {emne}: id brukt flere ganger: {', '.join(fd)}")
    flate_ids += [i for i in fi if i]
borte = sorted(set(reg) - set(ids) - set(flate_ids))
if borte: feil.append(f"- {len(borte)} id-er er slettet (skal skjules, aldri slettes): {', '.join(borte[:10])}")
uregistrert = sorted(set(i for i in ids + flate_ids if i) - set(reg))
if uregistrert: feil.append(f"- {len(uregistrert)} id-er står ikke i id-registeret (del dem ut med verktoy/matrikkel.py koble, verktoy/flater.py id, verktoy/vann.py lag eller verktoy/brygger.py maal)")
finnes = set(ids)
emneid = {'bygg': finnes}
for r in data('rettelser'):
    if 'i' in r: feil.append(f"- rettelse peker på plass i lista (i={r['i']}), ikke id"); break
    if r['emne'] not in emneid: emneid[r['emne']] = {x.get('id') for x in data(r['emne'], raa=True)}
    if r.get('id') not in emneid[r['emne']]: feil.append(f"- rettelse peker på {r['emne']}-id som ikke finnes: {r.get('id')}")
for emne in ('adresser', 'virksomheter'):
    for x in data(emne, raa=True):
        if x['bygg_id'] not in finnes: feil.append(f"- {emne} peker på bygg som ikke finnes: {x['bygg_id']}")
for emne in ('porter', 'legende'):
    for x in data(emne, raa=True):
        if 'bygg' in x: feil.append(f"- {emne} bruker plass i lista (bygg), ikke bygg_id"); break
        if x.get('bygg_id') is not None and x['bygg_id'] not in finnes: feil.append(f"- {emne} peker på id som ikke finnes: {x['bygg_id']}")
for x in b:
    if (x.get('id') or '').startswith('bnr-') and int(x['id'][4:]) not in [m['bygningsnummer'] for m in x.get('matrikkel', [])]:
        feil.append(f"- {x['id']}: bygningsnummeret står ikke i matrikkelfeltet")
gml = [x for x in b if x.get('gml')]
rapport('14_id', not feil, [f"{len(b)} bygg, {sum(1 for i in ids if i and i.startswith('bnr-'))} med bygningsnummer fra Matrikkelen "
                            f"({sum(1 for x in gml if x['id'].startswith('bnr-'))} av {len(gml)} i Gamlebyen), {len(reg)} id-er i registeret"] + feil)
