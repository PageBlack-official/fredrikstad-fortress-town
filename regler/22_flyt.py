"""Regel (29.10, oppdrag 15, Vegar: «overganger og flyt … så det oppfører seg slik brukeren forventer»): kameraet og kortet beveger seg
uten hopp, rykk og bråstopp, gester følger hånda, og tilbake går samme vei ut som inn. Målt bilde for bilde i bygget (verktoy/flyt-test.mjs)
med falsk klokke: 16 ms virtuell tid per bilde, så programvare-GPU-en her måler kontinuitet, ikke bildefrekvens. Bildefrekvens sjekkes i
ekte Chrome (tast d: «siste bevegelse … bilder/s»).
Mål per kamerabevegelse: hopp (et bilde som flytter over 2,5 ganger naboene og over 3 px) = 0, rykk (største endring i fart mellom to bilder
delt på toppfarten) <= 0,45, bråstopp (farten i siste bilde delt på toppfarten) <= 0,15."""
import subprocess, os, json, sys
from _felles import *
ut = os.path.join(ROT, 'rapport', 'flyt'); os.makedirs(ut, exist_ok=True)
p = os.path.join(ut, 'maaling.json')
r = subprocess.run(['node', os.path.join(ROT, 'verktoy', 'flyt-test.mjs'), os.path.join(ROT, 'ut', 'enkel', 'index.html'), p], capture_output=True, text=True, cwd=ROT, timeout=3000)
if r.returncode != 0 or not os.path.exists(p):
    rapport('22_flyt', False, ['- testen krasjet: ' + (r.stderr.strip()[-300:] or r.stdout.strip()[-300:])]); sys.exit()
d = json.load(open(p)); S = d['scenarier']; linjer = []; ok = True
def krav(navn, betingelse, tekst):
    global ok
    if not betingelse: ok = False
    linjer.append(f"- {'ok  ' if betingelse else 'FEIL'} {navn}: {tekst}")
def bevegelse(navn, m, rykk=0.45):
    if not m or not m.get('bilder'): krav(navn, False, 'ikke målt'); return
    if m['topp'] <= 2: krav(navn, False, f"kameraet flyttet seg ikke (topp {m['topp']} px/bilde)"); return
    krav(navn, m['hopp'] == 0 and m['rykk'] <= rykk and m['braastopp'] <= 0.15,
         f"{m['ms']} ms, topp {m['topp']} px/bilde, hopp {m['hopp']}, rykk {m['rykk']} (<= {rykk}), bråstopp {m['braastopp']} (<= 0,15)")
def tall(x, ellers=99): return ellers if x is None else x
def hopp_etter_start(m):
    # første bilde med bevegelse er gestens svar på fingeren (MapLibre gir hele utslaget med en gang); hopp telles etter det
    d = (m or {}).get('d') or []; f = next((i for i, v in enumerate(d) if v > 0.05), 0)
    return [i for i in (m or {}).get('hoppAt', []) if i > f]
def g(*k):
    v = S
    for n in k: v = v.get(n) if isinstance(v, dict) else None
    return v
bevegelse('klikk på hus, kameraet glir inn', g('klikk', 'inn'))
bevegelse('lukk kortet, kameraet glir tilbake', g('klikk', 'ut'))
krav('tilbake speiler inngangen (×)', tall(g('klikk', 'tilbakeAvvikPx')) <= 2, f"kameraet står {g('klikk', 'tilbakeAvvikPx')} px fra der det stod før klikket (<= 2)")
krav('Esc lukker kortet først og går samme vei ut', bool(g('esc', 'kortLukket')) and tall(g('esc', 'tilbakeAvvikPx')) <= 2, f"lukket {g('esc', 'kortLukket')}, {g('esc', 'tilbakeAvvikPx')} px fra start")
ki = [a for x in (g('klikk', 'kortInn') or []) if x['vis'] for a in x['anim']]; ku = [a for x in (g('klikk', 'kortUt') or []) if not x['vis'] for a in x['anim']]
krav('kortet glir inn og ut (ingen popp)', any('transform' in a['navn'] and a['ms'] >= 150 for a in ki) and any('transform' in a['navn'] and a['ms'] >= 100 for a in ku),
     'inn ' + ', '.join(f"{a['navn']} {a['ms']:.0f} ms" for a in ki) + '; ut ' + ', '.join(f"{a['navn']} {a['ms']:.0f} ms" for a in ku))
krav('desktop: sidepanel, huset synlig ved siden av', bool(g('klikk', 'kortSynlig')) and bool(g('klikk', 'sidepanel')) and bool(g('klikk', 'husSynligVedSidenAvKortet')), f"kort {g('klikk', 'kortRamme')}, hus på {g('klikk', 'husPx')}")
bevegelse('dobbeltklikk zoomer inn', g('dobbel', 'bevegelse'))
krav('dobbeltklikk: punktet under pekeren står', tall(g('dobbel', 'ankerPx')) <= 3 and (g('dobbel', 'zoom') or 0) >= 0.9, f"glipper {g('dobbel', 'ankerPx')} px, zoom +{g('dobbel', 'zoom')}")
m = g('hjul', 'bevegelse') or {}
krav('musehjul uten bråstopp', m.get('topp', 0) > 2 and m.get('braastopp', 9) <= 0.15, f"{m.get('ms')} ms, bråstopp {m.get('braastopp')}; hvert hakk gir et utslag (MapLibres hjulzoom, rykk {m.get('rykk')} måles ikke)")
krav('musehjul: punktet under pekeren står', tall(g('hjul', 'ankerPx')) <= 3 and (g('hjul', 'zoom') or 0) > 0.3, f"glipper {g('hjul', 'ankerPx')} px, zoom +{g('hjul', 'zoom')}")
o = g('dra', 'overlevering'); krav('dra og slipp: tregheten tar over farten', o is not None and 0.5 <= o <= 1.6 and g('dra', 'bevegelse', 'hopp') == 0, f"fart rett etter slipp / fart under dra = {o} (0,5–1,6), hopp {g('dra', 'bevegelse', 'hopp')}")
krav('hjem-glidningen kan avbrytes av et dra', (g('avbryt', 'glirVidereEtterSlipp') if g('avbryt', 'glirVidereEtterSlipp') is not None else 99) <= 2 and g('avbryt', 'bevegelse', 'hopp') == 0,
     f"etter slipp glir kameraet {g('avbryt', 'glirVidereEtterSlipp')} px/bilde (<= 2), hopp {g('avbryt', 'bevegelse', 'hopp')}, rundt avbruddet {g('avbryt', 'iAvbruddet')}")
bevegelse('hjem', g('hjem', 'bevegelse'))
m = g('intro', 'kameraFoerAvbrudd') or {}
krav('introen før avbrudd', m.get('topp', 0) > 2 and m.get('hopp') == 0 and m.get('rykk', 9) <= 0.45, f"topp {m.get('topp')} px/bilde, hopp {m.get('hopp')}, rykk {m.get('rykk')} (målt til avbruddet, så bråstopp gjelder ikke)")
krav('avbrutt intro: uskarpheten toner ut, hopper ikke', (g('intro', 'tiltHoppStorst') if g('intro', 'tiltHoppStorst') is not None else 9) <= 0.08 and (g('intro', 'tiltSlutt') or 0) <= 0.01,
     f"største endring per bilde {g('intro', 'tiltHoppStorst')} (<= 0,08), rundt avbruddet {g('intro', 'tiltVedAvbrudd')}, til slutt {g('intro', 'tiltSlutt')}")
bevegelse('mobil: trykk på hus, kameraet glir inn', g('mtrykk', 'inn'))
krav('mobil: bunnark, huset over kortet', bool(g('mtrykk', 'bunnark')) and bool(g('mtrykk', 'husOverKortet')), f"bunnark {g('mtrykk', 'bunnark')}, hus over kortet {g('mtrykk', 'husOverKortet')}, kort {g('mtrykk', 'kortRamme')}")
krav('mobil: dra kortet ned lukker det', bool(g('ark', 'lukket')) and (g('ark', 'folgerFingeren') or 0) > 40, f"kortet fulgte fingeren {g('ark', 'folgerFingeren')} px, lukket {g('ark', 'lukket')}")
krav('mobil: tilbake (Android/nettleser) lukker kortet', bool(g('tilbake', 'harHistorikk')) and bool(g('tilbake', 'kortLukket')), f"historikk {g('tilbake', 'harHistorikk')}, lukket {g('tilbake', 'kortLukket')}")
krav('mobil: klyp uten hopp', not hopp_etter_start(g('klyp', 'bevegelse')) and g('klyp', 'bevegelse', 'braastopp') is not None and g('klyp', 'bevegelse', 'braastopp') <= 0.15, f"hopp etter første svar {hopp_etter_start(g('klyp', 'bevegelse'))}, bråstopp {g('klyp', 'bevegelse', 'braastopp')} (fingeren starter og stopper bevegelsen; rykk måles ikke)")
krav('mobil: klyp zoomer rundt fingrene', tall(g('klyp', 'ankerPx')) <= 4 and (g('klyp', 'zoom') or 0) > 0.3, f"glipper {g('klyp', 'ankerPx')} px, zoom +{g('klyp', 'zoom')}")
krav('mobil: dobbelttrykk zoomer inn mot punktet', tall(g('mdobbel', 'ankerPx')) <= 3 and (g('mdobbel', 'zoom') or 0) >= 0.9, f"glipper {g('mdobbel', 'ankerPx')} px, zoom +{g('mdobbel', 'zoom')}")
rk = [a for x in (g('redusert', 'kortInn') or []) for a in x['anim']]
krav('redusert bevegelse: kortet toner, glir ikke', bool(g('redusert', 'kortVis')) and not g('redusert', 'kortGlir') and any('opacity' in a['navn'] for a in rk), ', '.join(f"{a['navn']} {a['ms']:.0f} ms" for a in rk) or 'ingen overgang')
krav('ingen JS-feil', not d['feil'], (d['feil'][0][:120] if d['feil'] else 'ingen'))
linjer.append('- Ikke målt her (må ses i ekte Chrome/telefon): bildefrekvens, styreflate-treghet fra macOS, iOS Safari-gester.')
rapport('22_flyt', ok, linjer)
