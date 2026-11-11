import { DATA, Q0 } from './00_oppsett.js';
// ---- gangtid langs gatene, fra gjestepartnerens bygg (?gjest=<id>) ----
// Hotellet (eller en annen partner, data/partnere.json) sitter i bygg_id; herfra regnes hvor langt det er å gå til hvert sted, PARKERING og
// turstart, målt langs gå-nettverket i data/veier.json (ikke i luftlinje: elva og kvartalene teller med). Alt følger partnerdataene, så et
// annet hotell får sine egne tall uten kodeendring. Uten ?gjest bygges ingenting og ingenting regnes – vanlig kart betaler ingenting.
// Nettet bygges først når noen spør (lat), og én Dijkstra fra hotellet gir avstanden til alle gatekryss; hvert sted snappes til nærmeste gate.
const GJEST = (DATA.partnere || []).find(p => p.id === Q0.get('gjest'));
const AKTIV = !!(GJEST && GJEST.bygg_id);
const FART = 5000 / 60;   // rolig vandring: 5 km/t = 83 m/min (en hotellgjest, ikke en jogger)

let kart = null;   // null = ikke bygd ennå · false = kunne ikke bygges · ellers {dist, snap}
const memo = new Map();   // meter per punkt (x,y avrundet): søket spør om de samme stedene for hvert tastetrykk

function bygg(){
  if (!AKTIV) return (kart = false);
  const b = (DATA.bygg || []).find(x => x.id === GJEST.bygg_id);
  if (!b || !b.p || !b.p.length) return (kart = false);
  let cx = 0, cy = 0; for (const [x, y] of b.p) { cx += x; cy += y; } cx /= b.p.length; cy /= b.p.length;   // hotellets midtpunkt

  // gå-nettverket: hvert punkt i veilinjene blir en node (slått sammen på 0,1 m der linjene deler et kryss), hvert ledd en kant med lengde i meter
  const idx = new Map(), adj = [], segs = [];
  const nid = (x, y) => { const k = Math.round(x * 10) + ',' + Math.round(y * 10); let i = idx.get(k); if (i === undefined) { i = adj.length; idx.set(k, i); adj.push([]); } return i; };
  for (const v of (DATA.veier || [])) { const p = v.p || []; for (let i = 0; i < p.length - 1; i++) {
    const ax = p[i][0], ay = p[i][1], bx = p[i + 1][0], by = p[i + 1][1];
    const a = nid(ax, ay), bb = nid(bx, by), w = Math.hypot(bx - ax, by - ay);
    adj[a].push([bb, w]); adj[bb].push([a, w]); segs.push({ ax, ay, bx, by, a, b: bb }); } }

  // snap: nærmeste punkt på nettet, med avstanden dit (off) og langs kanten til hver ende (dA, dB)
  const snap = (x, y) => {
    let best = null, bo = Infinity;
    for (const s of segs) { const dx = s.bx - s.ax, dy = s.by - s.ay, L2 = dx * dx + dy * dy;
      const t = L2 ? Math.max(0, Math.min(1, ((x - s.ax) * dx + (y - s.ay) * dy) / L2)) : 0;
      const px = s.ax + t * dx, py = s.ay + t * dy, off = Math.hypot(x - px, y - py);
      if (off < bo) { bo = off; best = { off, a: s.a, b: s.b, dA: Math.hypot(px - s.ax, py - s.ay), dB: Math.hypot(px - s.bx, py - s.by) }; } }
    return best;
  };

  const start = snap(cx, cy); if (!start) return (kart = false);
  // Dijkstra fra hotellet (binær haug), sådd fra begge endene av gata hotellet står ved
  const dist = new Float64Array(adj.length).fill(Infinity), heap = [];
  const opp = (i) => { while (i > 0) { const p = (i - 1) >> 1; if (heap[p][0] <= heap[i][0]) break; [heap[p], heap[i]] = [heap[i], heap[p]]; i = p; } };
  const ned = () => { let i = 0; for (;;) { let s = i; const l = 2 * i + 1, r = 2 * i + 2; if (l < heap.length && heap[l][0] < heap[s][0]) s = l; if (r < heap.length && heap[r][0] < heap[s][0]) s = r; if (s === i) break; [heap[s], heap[i]] = [heap[i], heap[s]]; i = s; } };
  const saa = (n, d) => { if (d < dist[n]) { dist[n] = d; heap.push([d, n]); opp(heap.length - 1); } };
  saa(start.a, start.off + start.dA); saa(start.b, start.off + start.dB);
  while (heap.length) { const [d, u] = heap[0]; const last = heap.pop(); if (heap.length) { heap[0] = last; ned(); }
    if (d > dist[u]) continue; for (const [v, w] of adj[u]) { const nd = d + w; if (nd < dist[v]) { dist[v] = nd; heap.push([nd, v]); opp(heap.length - 1); } } }
  return (kart = { dist, snap });
}

// meter å gå langs gatene fra hotellet til (x, y); Infinity om stedet ikke nås langs nettet
function meter(x, y){
  if (!AKTIV) return Infinity;
  const n = Math.round(x * 10) + ',' + Math.round(y * 10); if (memo.has(n)) return memo.get(n);
  if (kart === null) bygg();
  let m = Infinity;
  if (kart) { const s = kart.snap(x, y); if (s) m = s.off + Math.min(kart.dist[s.a] + s.dA, kart.dist[s.b] + s.dB); }
  memo.set(n, m); return m;
}
// minutter rolig gange, aldri under 1; null om stedet ikke nås
function minutter(x, y){ const m = meter(x, y); return isFinite(m) ? Math.max(1, Math.round(m / FART)) : null; }
// kort tekst til kort og treff: «8 min å gå» (null om ikke nås)
function tekst(x, y){ const n = minutter(x, y); return n == null ? null : `${n} min å gå`; }
// hører stedet til hotellet selv? (da gir vi ingen gangtid – du er der)
function eier(bygg_id){ return AKTIV && bygg_id === GJEST.bygg_id; }

// gående person, samme strek som nålene i søket
const IKON = '<svg class="gangikon" viewBox="0 0 24 24" width="15" height="15" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="13" cy="4.5" r="1.8"/><path d="M12.2 8.3 9 10.5l1.8 3.2 1.1 6.6M12.2 8.3l3.4 1.3 2.1 3.1M12.2 8.3 8.4 20M10.8 13.7l-3.2 2.1-2.1 3.4"/></svg>';

export const GANGE = { aktiv: AKTIV, gjest: GJEST, minutter, tekst, meter, eier, IKON };
