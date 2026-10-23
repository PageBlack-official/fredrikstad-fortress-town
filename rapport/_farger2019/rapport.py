"""Kontrollark, palett, avviksliste og md-rapport fra farger2019.json."""
import sys, os, json, collections
HER = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HER)
from felles2019 import *
from PIL import ImageDraw, ImageFont

UT = os.path.join(ROT, 'soc/rapport')
f = json.load(open(os.path.join(UT, 'farger2019.json')))
b = last_bygg()

# ---- kontrollark
im = Image.open(os.path.join(ROT, 'kilder2019/brosjyre2019-3.jpg')).convert('RGB')
S = 1600 / im.width
im = im.resize((1600, round(im.height * S)), Image.LANCZOS)
dr = ImageDraw.Draw(im)
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 9)
for i, x in enumerate(b):
    r = f[str(i)]
    if not r.get('px2019'):
        continue
    px, py = r['px2019'][0] * S, r['px2019'][1] * S
    if not (0 <= px < im.width and 0 <= py < im.height):
        continue
    if r.get('tak'):
        dr.ellipse([px - 7, py - 7, px + 7, py + 7], fill=tuple(r['tak']), outline=(0, 0, 0))
        if r.get('vegg'):
            dr.ellipse([px - 3, py - 3, px + 3, py + 3], fill=tuple(r['vegg']), outline=(40, 40, 40))
        if r['sikkerhet'] == 'lav':
            dr.ellipse([px - 9, py - 9, px + 9, py + 9], outline=(255, 140, 0), width=1)
    else:
        dr.ellipse([px - 6, py - 6, px + 6, py + 6], outline=(255, 0, 255), width=2)
    dr.text((px + 8, py - 5), str(i), fill=(0, 0, 0), font=font)
im.save(os.path.join(UT, 'farger2019-kontrollark.png'))

# ---- tall
stat = collections.Counter(r['sikkerhet'] for r in f.values() if r.get('tak'))
kilde = collections.Counter(r.get('kilde') for r in f.values() if r.get('tak'))
n_i = sum(1 for r in f.values() if r.get('tak'))
n_ikke = sum(1 for r in f.values() if not r.get('tak'))
utenfor = [k for k, r in f.items() if not r.get('tak') and 'utenfor' in r['merknad']]
innenfor_ikke = [k for k, r in f.items() if not r.get('tak') and 'utenfor' not in r['merknad'] and 'skjult' not in r['merknad'] and 'uten fotavtrykk' not in r['merknad']]


def klynger(vals, tol=8):
    ut = []
    for col, n in vals.most_common():
        for k in ut:
            if naer(col, k[0], tol):
                k[1] += n; break
        else:
            ut.append([col, n])
    ut.sort(key=lambda k: -k[1])
    return [(tuple(c), n) for c, n in ut]


pal = {}
for felt in ('tak', 'taks', 'vegg', 'veggs'):
    c = collections.Counter(tuple(r[felt]) for r in f.values() if r.get(felt))
    pal[felt] = klynger(c)

# ---- kalibrering
def kal(tol=15):
    nt = tt = nv = tv = 0
    miss_t = []
    for i, x in enumerate(b):
        r = f[str(i)]
        if x.get('taks') and x.get('tak') and r.get('tak'):
            nt += 1
            hit = naer(r['tak'], x['tak'], tol) or naer(r['tak'], x['taks'], tol) or (r.get('taks') and (naer(r['taks'], x['taks'], tol) or naer(r['taks'], x['tak'], tol)))
            tt += bool(hit)
            if not hit: miss_t.append(i)
        if x.get('veggs') and x.get('vegg') and r.get('vegg'):
            nv += 1
            if naer(r['vegg'], x['vegg'], tol) or naer(r['vegg'], x['veggs'], tol) or (r.get('veggs') and (naer(r['veggs'], x['veggs'], tol) or naer(r['veggs'], x['vegg'], tol))): tv += 1
    return nt, tt, nv, tv, miss_t

nt, tt, nv, tv, miss_t = kal(15)
# per sikkerhet
per_sik = {}
for sik in ('høy', 'middels', 'lav'):
    n = t = 0
    for i, x in enumerate(b):
        r = f[str(i)]
        if r['sikkerhet'] == sik and x.get('taks') and r.get('tak'):
            n += 1
            if naer(r['tak'], x['tak'], 15) or naer(r['tak'], x['taks'], 15) or (r.get('taks') and naer(r['taks'], x['taks'], 15)): t += 1
    per_sik[sik] = (t, n)

# misser: dagens standardverdi?
STD = [(244, 120, 104), (246, 122, 106)]
miss_std = sum(1 for i in miss_t if any(naer(b[i]['tak'], s, 3) for s in STD))
miss_graa = sum(1 for i in miss_t if any(naer(b[i]['tak'], s, 3) for s in [(188, 188, 192), (190, 190, 194), (128, 128, 132)]))

# ---- avvik > 20 per kanal (vegg eller tak)
avvik = []
for i, x in enumerate(b):
    r = f[str(i)]
    if not r.get('tak') or not x.get('tak'):
        continue
    dt = max(abs(int(a) - int(c)) for a, c in zip(r['tak'], x['tak']))
    dv = max(abs(int(a) - int(c)) for a, c in zip(r['vegg'], x['vegg'])) if r.get('vegg') and x.get('vegg') else 0
    if dt > 20 or dv > 20:
        avvik.append((i, x.get('navn') or '', x['tak'], r['tak'], x['vegg'], r.get('vegg'), r['sikkerhet'], r['kilde']))

md = []
md.append('# Fargeregister fra 2019-brosjyren — FORSLAG (ikke lagt inn)\n')
md.append('Kilde: kilder2019/brosjyre2019-3.jpg (2480×1754, norsk kartside; -1 og -5 er samme kart på andre språk, -2/-4/-6 er tekstsider). Vegar: «alle hus er farget korrekt» der. Takene har ingen regel; de er lest som de er.\n')
md.append('Filer: soc/rapport/farger2019.json (register), soc/rapport/farger2019-kontrollark.png (samplepunkter), soc/rapport/farger2019-ark/ (per kvartal), kode i soc/rapport/_farger2019/ (registrer.py, kvartaldel.py, hoved.py, rapport.py, ark.py).\n')
md.append('## Metode\n')
md.append('1. **Registrering.** 2019-JPG-en er den samme tegningen som 2015-trykket (pdf/side300-1.png) i halv oppløsning. ORB + RANSAC (similaritet) gir 2015-px → 2019-px: skala 0,49976, rotasjon 0,01°, forskyvning (0,60, 0,14) px, residual median 0,7 px. Lagret i _farger2019/reg2015til2019.npy. Dermed virker affin2 (modell → 2015-px) og kvartaltegningenes plassering (kvartal/vek/plassering.json) rett inn i 2019-bildet.')
md.append('2. **Del A, hus med kvartaltegning (%d hus).** Kvartaltegningene er utsnitt av samme vektortegning, plassert i trykket med skala/forskyvning som stemmer på ±1 px. For hver fasade som kvartal/ut/kobling-*.json kobler til et modellbygg, legges veggpolygonet (tegning-pt → trykk → 2019-px) på 2019-bildet og den dominerende fargen leses (grov kvantisering, største klynge, median; svart strek, grønt (trær/plen) og vann hoppes over). Takflater = de flatene av typen «tak» i kvartaltegningen som grenser til veggens overkant (buffer 1,6 pt, sentrum over veggen). Kantstykker som stikker ut av arket (avkuttede nabohus) hoppes over. Vegger grupperes etter retning (basekant faller mot venstre/høyre): lysest = vegg, mørkest = veggs hvis samme kulør. Tak = tyngste klynge (piksler × kontaktlengde); er den mørk og en lysere flate har ≥25 %% av vekten, er den mørke skyggesiden (taks). Kvartaltegningens egen fyllfarge brukes som kryssjekk per flate (se Kryssjekk).' % kilde.get('2019+kvartaltegning', 0))
md.append('3. **Del B, resten innenfor arket (%d hus).** Som forrige forsøk (soc/rapport/_farger/kjor.py): 2015-trykkets vektorflater rastrert til etikettbilde, fotavtrykket projisert med affin2 + lokal korreksjon og flyttet (±48 px, pluss 4·h i høyden) til flest punkter lander på husflater. Nytt: fargen leses ikke fra 2015-vektoren, men fra 2019-bildet innenfor den samme flaten. Takflate = flaten med flest fotavtrykkspunkter; vegg = første husflate under synlige kanter. Sikkerhet maks «middels» her, fordi husene er tegnet fritt og ren forskyvning kan treffe nabohuset.' % kilde.get('2019', 0))
md.append('4. **Skyggetoner.** Der tak eller vegg er funnet uten skyggeflate, er taks/veggs hentet fra det vanligste paret i registeret for samme lysfarge (merket «utledet fra palettpar» i merknaden).\n')
md.append('## Kryssjekk 2019 ↔ kvartaltegning\n')
md.append('Kvartaltegningene har fyllfarger som RGB (3 verdier) eller CMYK (4 verdier). RGB-verdiene treffer 2019-bildet direkte (f.eks. (206,129,63) i tegningen = (205,130,63) i 2019). CMYK-verdiene er oversatt med et oppslag bygd av de sikre prøvene (andel > 0,5, > 150 px): (0, .648, .551, 0) → (240,120,103), (.205, .64, .608, .167) → (180,103,85), (0,0,0,.3) → (198,198,198) osv. (_farger2019/cmyk-oppslag.json). Per flate: enig (±15) → flaten teller fullt; uenig og 2019 tydelig (andel ≥ 0,45, ≥ 120 px) → 2019 velges med vekt 0,6; uenig og 2019 utydelig (trær, symboler, tekst over) → kvartaltegningens farge med vekt 0,3. **2019 vinner der den er lesbar**, fordi det er Vegars fasit; kvartaltegningen brukes der 2019 er dekket. Uenighet skyldes nesten alltid at noe ligger over huset i 2019 (trær, tegnforklaringssirkler, symboler), eller at koblingen fasade→bygg har tatt nabohuset.\n')
md.append('## Kalibrering mot dagens bygg.vegg/tak (hus med veggs/taks i dag)\n')
md.append('- Tak: %d av %d = **%.0f %%** (±15 per kanal; treff hvis forslagets tak/taks treffer dagens tak/taks).' % (tt, nt, 100 * tt / max(1, nt)))
md.append('- Vegg: %d av %d = **%.0f %%**.' % (tv, nv, 100 * tv / max(1, nv)))
md.append('- Per sikkerhet (tak): ' + ', '.join('%s %d/%d' % (k, v[0], v[1]) for k, v in per_sik.items()) + '.')
md.append('- **Målet på 85 %% er ikke nådd, og jeg tror ikke det kan nås mot denne fasiten.** Av de %d bommene har %d dagens standardverdi rødt tak (244/246,120,104) og %d dagens grått (188/190/128). Kontrollarket og utsnittene i _farger2019/chk-miss.png viser at 2019-tegningen faktisk har grått tak der dagens verdi sier rødt (f.eks. bygg 194, 206, 226, 313) og rødt der dagens sier grått (168, 208, 218, 355, 380). Dagens verdier er i stor grad standardverdier (145 hus har nøyaktig (244,120,104)), ikke avlest trykk. 2019-bildet er fasiten Vegar ba om; der registeret og dagens verdi er uenige, er det dagens verdi som bør byttes, ikke forslaget. Uavhengig sjekk: for de 28 husene med tegnforklaringsnummer (sirkelen sitter på taket) stemmer forslaget med fargen rundt sirkelen for de store, frittliggende husene (Tøihuset, Provianthuset, Laboratoriet, Bakeriet, Ekserserhuset, Arnesgården, Det gamle rådhus, Rosinggården, Bullgården); bommene der er hus der sirkelen sitter på skyggesiden eller på en nabo.' % (len(miss_t), miss_std, miss_graa))
md.append('- Det som fortsatt er usikkert: Del B-husene (ren forskyvning) i de tette kvartalene uten kvartaltegning, og hus der koblingen fasade→bygg i kvartal/ut/kobling-*.json har tatt nabohuset (det gir riktig farge for feil hus).\n')
md.append('## Antall\n')
md.append('- Hus i modellen: %d. Med farge i registeret: %d (høy %d, middels %d, lav %d). Kilde: %s.' % (len(b), n_i, stat.get('høy', 0), stat.get('middels', 0), stat.get('lav', 0), ', '.join('%s %d' % kv for kv in kilde.items())))
md.append('- Ikke i trykket: %d, hvorav %d utenfor arket (gml=0), 9 skjult, og %d innenfor arket uten lesbar husflate: %s.\n' % (n_ikke, len(utenfor), len(innenfor_ikke), ', '.join(innenfor_ikke)))
md.append('## Palett i 2019 (klynger ±8, antall hus)\n')
for felt, tittel in (('tak', 'Tak (lys side)'), ('taks', 'Tak (skyggeside)'), ('vegg', 'Vegg (lys side)'), ('veggs', 'Vegg (skyggeside)')):
    md.append('**%s**\n' % tittel)
    for col, n in pal[felt]:
        if n >= 1:
            md.append('- rgb%s — %d hus' % (str(col), n))
    md.append('')
md.append('## Hus der 2019 avviker fra dagens bygg.vegg/tak med mer enn 20 per kanal (%d hus)\n' % len(avvik))
md.append('| bygg | navn | tak i dag | tak 2019 | vegg i dag | vegg 2019 | sikkerhet | kilde |')
md.append('|---|---|---|---|---|---|---|---|')
for a in avvik:
    md.append('| %d | %s | %s | %s | %s | %s | %s | %s |' % (a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7]))
md.append('')
md.append('## Hva Vegar bør se på\n')
md.append('1. Kontrollarket: stor sirkel = tak, liten = vegg, magenta ring = ikke funnet, oransje ring = lav sikkerhet. Nummer = byggindeks.')
md.append('2. Paletten over: er dette fargene han vil ha i modellen? Klyngene ±8 kan slås sammen til faste palettverdier før registeret blir data/farger.json.')
md.append('3. Avvikslista: der dagens verdi er en standardverdi og 2019 sier noe annet, bør 2019 vinne.')
open(os.path.join(UT, 'farger2019.md'), 'w').write('\n'.join(md))
print('tak %d/%d vegg %d/%d; i trykket %d; avvik %d; palett tak %d klynger' % (tt, nt, tv, nv, n_i, len(avvik), len(pal['tak'])))
print(per_sik, 'miss std', miss_std, 'miss grå', miss_graa, 'av', len(miss_t))
