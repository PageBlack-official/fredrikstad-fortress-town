"""Skriv traer-flyfoto.json (+ meta), sammenligning i 50 m-rutenett, og tall til rapporten."""
import cv2, numpy as np, json, math
from collections import Counter
ROT = '/tmp/claude-0/-home-claude/906a72dc-ab38-5838-984d-9da0bf1a01a5/scratchpad/soc'
UT = '/tmp/claude-0/-home-claude/906a72dc-ab38-5838-984d-9da0bf1a01a5/scratchpad/trearbeid'
RAP = ROT + '/rapport'
im = cv2.imread(ROT + '/kilder/flyfoto-google-2026-10-23.jpg'); Hh, Ww = im.shape[:2]
V = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)[..., 2]
valid = (V > 12).astype(np.uint8); valid_er = cv2.erode(valid, np.ones((9, 9), np.uint8))
k = json.load(open(ROT + '/kilder/flyfoto-google-2026-10-23.json')); a = k['anker']; ax, ay = a['px']; kx, ky = a['modell_xy']; mpp = a['m_per_px_oversikt']; F = a['forstorrelse']; O = a['forskyvning']
MPP = mpp / F
def px(x, y): return (F * (ax + (x - kx) / mpp) + O, F * (ay - (y - ky) / mpp) + O)
def inv(u, v): return (kx + ((u - O) / F - ax) * mpp, ky - ((v - O) / F - ay) * mpp)
ut = json.load(open(UT + '/kroner_raa.json')); bort = json.load(open(UT + '/bort.json')); sol = json.load(open(UT + '/sol.json'))
gamle = json.load(open(ROT + '/data/traer.json'))
def dekket(x, y):
    u, v = px(x, y); u, v = int(u), int(v)
    return 0 <= u < Ww and 0 <= v < Hh and valid_er[v, u] > 0
g_inne = [p for p in gamle if dekket(p[0], p[1])]; g_ute = [p for p in gamle if not dekket(p[0], p[1])]
# dekningsområdet i modellmeter
ys, xs = np.nonzero(valid_er > 0); x_min, y_max = inv(xs.min(), ys.min()); x_max, y_min = inv(xs.max(), ys.max())
nye = [[t['x'], t['y'], t['s'], t['bakke'], t['sik']] for t in ut]
beholdt = [[p[0], p[1], p[2], p[3], 0.2] for p in g_ute]  # utenfor fotoet: gamle punkter, lav sikkerhet
alle = nye + beholdt
json.dump(alle, open(RAP + '/traer-flyfoto.json', 'w'), separators=(',', ':'))
# 50 m-rutenett: nye vs gamle innenfor dekningen
def rute(p): return (int(math.floor(p[0] / 50)), int(math.floor(p[1] / 50)))
cn = Counter(rute(t) for t in nye); cg = Counter(rute(p) for p in g_inne)
ruter = sorted(set(cn) | set(cg))
rader = []
for r in ruter:
    n, g = cn.get(r, 0), cg.get(r, 0)
    rader.append((r, n, g, g - n))
for_mange = sorted([x for x in rader if x[3] >= 10], key=lambda x: -x[3])
for_faa = sorted([x for x in rader if x[3] <= -10], key=lambda x: x[3])
Hs = [t['H'] for t in ut]; Ds = [t['D'] for t in ut]; ss = [t['s'] for t in ut]
hist = Counter(min(int(h // 3) * 3, 15) for h in Hs)
meta = {
    'kilde': 'kilder/flyfoto-google-2026-10-23.jpg (Google Maps, skjermbilder 23.10.2026), transform fra kilder/flyfoto-google-2026-10-23.json',
    'metode': 'HSV-vegetasjon (H 30-95, S>45, ExG>10) → trekroner = tekstur (lokal std i V, 7x7, glattet, >11) og mørkere enn plen (V<125) → '
              'avstandstransform, topper med min. 3,5 m avstand, Voronoi-celler rundt toppene, felt bredere enn 11 m delt med k-means i kroner på ca. 7,6 m → '
              'filtrert mot hus (bygg.json +1 m), kjørevei (landskap.veier k=kjore, 0,8 x bredde) og vann lest fra fotoet; punkt inntil 2,5-3 m inne flyttes ut, lenger inne forkastes.',
    'felt': '[x, y, s, bakke, sikkerhet]: x øst, y nord i modellmeter; s = størrelse som i 12_trær.js (kronediameter ≈ 2,3·s, kronetopp ≈ 2,4·s); bakke = terrenghøyde fra landskap.terreng; sikkerhet 0,1-1,0 (0,2 = gammelt punkt utenfor fotoet, beholdt)',
    's_omregning': 's = (D/2,3 + H/2,4)/2 der D = kronediameter fra kroneareal (D = 2·sqrt(A/π)) og H = anslått høyde; klemt til 1,6-7,5',
    'hoyde': 'H = 1,2·D (løvtrær); der skyggen var målbar (ingen annen krone/hus/vann i skyggeretningen) ble H satt til snittet av skyggehøyden og 1,2·D',
    'sol': {'skyggeretning_bildevinkel': sol['bildevinkel_grader'], 'skyggelengde_per_m_hoyde': round(sol['L_per_h'], 2), 'solhoyde_grader': round(math.degrees(math.atan(1 / sol['L_per_h'])), 1), 'fra_n_bygg': sol['n']},
    'm_per_px': MPP,
    'dekning_modell': {'x': [round(x_min), round(x_max)], 'y': [round(y_min), round(y_max)], 'merknad': 'Isegran og sørvollene (y < ca. -250) er ikke med i fotoet'},
    'antall': {'kroner_fra_foto': len(nye), 'gamle_punkter_utenfor_foto_beholdt': len(beholdt), 'totalt': len(alle),
               'gamle_i_dekket_omrade': len(g_inne), 'gamle_totalt': len(gamle), 'forkastet': bort,
               'hoy_sikkerhet': sum(1 for t in ut if t['sik'] >= 0.7), 'delt_med_kmeans': sum(1 for t in ut if t['delt']), 'skygge_brukt': sum(1 for t in ut if t['kilde'] != 'diameter')},
    'dato': '2026-10-23', 'laget_av': 'Claude (treregister fra flyfoto), forslag – ikke lagt inn i data/',
}
json.dump(meta, open(RAP + '/traer-flyfoto.meta.json', 'w'), ensure_ascii=False, indent=1)
print(json.dumps(meta['antall'], ensure_ascii=False))
print('H percentiler', np.percentile(Hs, [5, 25, 50, 75, 95]).round(1), 'hist', sorted(hist.items()))
print('D percentiler', np.percentile(Ds, [5, 25, 50, 75, 95]).round(1), 's', np.percentile(ss, [5, 25, 50, 75, 95]).round(2))
print('gamle s snitt', np.mean([p[2] for p in gamle]).round(2))
print('ruter', len(ruter), 'for mange gamle (>=10 flere):', len(for_mange), 'for få gamle (>=10 færre):', len(for_faa))
print('FOR MANGE', for_mange[:12]); print('FOR FÅ', for_faa[:12])
print('dekning', meta['dekning_modell'])
print('på voll (bakke>1 m)', sum(1 for t in ut if t['bakke'] > 1.0))
hs_par = [(t['Hs'], 1.2 * t['D']) for t in ut if t['Hs']]
print('skygge vs 1,2D median', np.median([p[0] for p in hs_par]), np.median([p[1] for p in hs_par]), 'n', len(hs_par))
