import * as THREE from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { DATA, Q0, map, scene } from './00_oppsett.js';
import { mat } from './05_bygg.js';
// ---- festivaler: plassen gjøres om når det er festival der (Vegar: «Månefestivalen … hele Tøihusplassen omgjøres med scene, lysshow») ----
// Arrangementene står i data/arrangementer.json: navn, plass, fra/til (datoer) eller regel, scenens plass og retning, publikum, boder. Kartet viser
// festivalen fra kvelden før første dag til siste dag er over; ?festival=<id> viser den uansett dato (til visning), ?festival=0 aldri.
// Scenen er bygd som husene (samme strek og skygge); lysene og skjermen er egne, ulyste stoffer som ikke tegner strek.
const ARR = DATA.arrangementer || [];
const tving = Q0.get('festival');
const idag = new Date();
// datoene: fra/til i dataene, eller regelen «siste-helg-i-juli» (torsdag til lørdag i helgen med julis siste lørdag) for andre år
function datoer(a, aar){
  if (a.fra && a.til && +a.fra.slice(0, 4) === aar) return [new Date(a.fra + 'T00:00:00'), new Date(a.til + 'T23:59:59')];
  if (a.regel === 'siste-helg-i-juli') { const l = new Date(aar, 6, 31); l.setDate(31 - ((l.getDay() + 1) % 7)); const f = new Date(l); f.setDate(l.getDate() - 2); l.setHours(23, 59, 59); return [f, l]; }
  return null;
}
const aktiv = tving === '0' ? null : ARR.find(a => a.id === tving) || (tving ? null : ARR.find(a => {
  const d = datoer(a, idag.getFullYear()); if (!d) return false; const fra = new Date(d[0]); fra.setHours(fra.getHours() - 6); return idag >= fra && idag <= d[1]; }));
let anim = null;
if (aktiv) anim = bygg(aktiv);

function bygg(a){
  const S = a.scene, g = new THREE.Group(); g.name = 'festival-' + a.id;
  const M = { gulv: mat([40, 38, 42], false), stål: mat([70, 72, 78], false), høyttaler: mat([28, 28, 30], false), telt: mat([235, 232, 222], false) };
  const kloss = (dx, dy, dz, x, y, z, m, gr = g) => { const k = new THREE.Mesh(new THREE.BoxGeometry(dx, dy, dz), m); k.position.set(x, y, z); k.castShadow = k.receiveShadow = true; gr.add(k); return k; };
  // scenen bygges med fronten mot +x og dreies til retningen i dataene
  const sc = new THREE.Group(); g.add(sc);
  const B = S.bredde, D = S.dybde, H = 7.5;
  kloss(D, 1.2, B, 0, 0.6, 0, M.gulv, sc);                                         // scenegulvet
  for (const z of [-B / 2, B / 2]) for (const x of [-D / 2, D / 2]) kloss(0.35, H, 0.35, x, H / 2, z, M.stål, sc);   // tårnene
  kloss(D + 0.6, 0.5, B + 0.6, 0, H, 0, M.stål, sc);                               // takrammen
  kloss(D * 0.9, 0.3, B * 0.95, 0, H + 0.6, 0, M.telt, sc);                        // taket
  for (const z of [-B / 2 - 1.6, B / 2 + 1.6]) kloss(1.4, 5, 1.4, D / 2 - 0.4, 2.5, z, M.høyttaler, sc);   // høyttalertårn
  // skjermen bak bandet: et sakte fargeskift (ulyst, ingen strek)
  const skjermU = { tid: { value: 0 } };
  const skjerm = new THREE.Mesh(new THREE.PlaneGeometry(B * 0.8, 4.2), new THREE.ShaderMaterial({ uniforms: skjermU, depthWrite: true, side: THREE.DoubleSide,
    vertexShader: 'varying vec2 vU; void main(){ vU=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }',
    fragmentShader: `uniform float tid; varying vec2 vU; void main(){ float m=0.5+0.5*sin(vU.x*6.+tid*0.8)*cos(vU.y*4.-tid*0.6);
      vec3 c=mix(vec3(0.95,0.78,0.30), vec3(0.20,0.25,0.75), m); c=mix(c, vec3(0.85,0.35,0.55), 0.5+0.5*sin(tid*0.3)); gl_FragColor=vec4(c*0.95,1.); }` }));
  skjerm.position.set(-D / 2 + 0.3, 1.2 + 2.6, 0); skjerm.rotation.y = Math.PI / 2; sc.add(skjerm);
  // lyskjeglene: åtte strålende kjegler fra takrammen som feier over publikum (additivt, uten dybde)
  const straler = [];
  const strMat = c => new THREE.ShaderMaterial({ transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide, uniforms: { farge: { value: new THREE.Color(c) }, styrke: { value: 0.55 } },
    vertexShader: 'varying float vY; void main(){ vY=position.y; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }',
    fragmentShader: 'uniform vec3 farge; uniform float styrke; varying float vY; void main(){ float a=smoothstep(-28.,0.,vY); gl_FragColor=vec4(farge*styrke*a*a, 1.); }' });
  const kjegle = new THREE.ConeGeometry(2.6, 28, 24, 1, true); kjegle.translate(0, -14, 0);   // spissen i origo, åpningen 28 m ut
  const farger = [0xffd27a, 0x8fb6ff, 0xff7fb2, 0xffffff];
  for (let i = 0; i < 8; i++) { const z = -B / 2 + (i + 0.5) * B / 8; const p = new THREE.Group(); p.position.set(D / 2 - 0.2, H - 0.3, z);
    const s = new THREE.Mesh(kjegle, strMat(farger[i % 4])); s.renderOrder = 10; p.add(s); sc.add(p); straler.push({ p, fase: i * 0.7 }); }
  sc.position.set(S.x, 0, -S.y); sc.rotation.y = (S.retning || 0) * Math.PI / 180;
  // publikum: små skikkelser i fire farger, tettest foran scenen
  const P = a.publikum, fig = new THREE.CylinderGeometry(0.22, 0.26, 1.7, 6); fig.translate(0, 0.85, 0);
  const fargerP = [[196, 74, 62], [60, 86, 140], [222, 196, 120], [72, 120, 92]], per = Math.ceil(P.antall / 4), m4 = new THREE.Matrix4();
  const front = new THREE.Vector3(1, 0, 0).applyAxisAngle(new THREE.Vector3(0, 1, 0), sc.rotation.y);   // scenens front i verden
  let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  // én sammenslått flate per farge (husstoffet tegner ikke instanser)
  fargerP.forEach(f => { const deler = []; let n = 0;
    for (let t = 0; t < per * 6 && n < per; t++) { const x = P.x0 + rnd() * (P.x1 - P.x0), y = P.y0 + rnd() * (P.y1 - P.y0);
      const d = (x - S.x) * front.x + (-y + S.y) * front.z; if (d < D / 2 + 1.5) continue;              // ikke på eller bak scenen
      if (rnd() > Math.exp(-(d - D / 2) / 70)) continue;                                                // tettere nær scenen
      deler.push(fig.clone().applyMatrix4(m4.makeTranslation(x, 0.05, -y))); n++; }
    if (!deler.length) return; const m = new THREE.Mesh(mergeGeometries(deler), mat(f, false)); m.castShadow = m.receiveShadow = true; g.add(m); });
  // boder (Månehagen): små telt med farget tak der maten er
  if (a.boder) { const Bd = a.boder, takF = [[196, 74, 62], [236, 226, 206], [60, 86, 140]];
    for (let k = 0; k < Bd.antall; k++) { const x = Bd.x0 + (k + 0.5) * (Bd.x1 - Bd.x0) / Bd.antall, y = Bd.y0 + (k % 2 ? 0.25 : 0.75) * (Bd.y1 - Bd.y0);
      kloss(3, 2.2, 3, x, 1.1, -y, M.telt); kloss(3.4, 0.5, 3.4, x, 2.45, -y, mat(takF[k % 3], false)); } }
  // lyslenker over plassen: små lys på tråder fra scenen og utover
  const lysPos = []; for (let k = 0; k < 6; k++) { const ang = (k - 2.5) * 0.28; for (let j = 0; j <= 24; j++) { const t = j / 24, r = D / 2 + t * 40;
    const lx = r * Math.cos(ang), lz = r * Math.sin(ang), h = 6.5 - Math.sin(t * Math.PI) * 1.6; lysPos.push(new THREE.Vector3(lx, h, lz).applyAxisAngle(new THREE.Vector3(0, 1, 0), sc.rotation.y).add(new THREE.Vector3(S.x, 0, -S.y))); } }
  const lysGeo = new THREE.BufferGeometry().setFromPoints(lysPos);
  const lys = new THREE.Points(lysGeo, new THREE.PointsMaterial({ color: 0xffe2a0, size: 0.9, sizeAttenuation: true, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending }));
  g.add(lys);
  scene.add(g);
  return { g, straler, skjermU, a };
}

// lysshowet: strålene feier, skjermen skifter. Kartet tegnes da 30 ganger i sekundet så lenge festivalen er i bildet og fanen er synlig.
if (anim) {
  const t0 = performance.now(); let sist = 0;
  const steg = naa => {
    if (!document.hidden && naa - sist > 33) { sist = naa; const t = (naa - t0) / 1000; anim.skjermU.tid.value = t;
      // strålene peker fra rett fram og opp mot himmelen over publikum, og vugger sideveis
      for (const s of anim.straler) { s.p.rotation.z = Math.PI / 2 + 0.45 + 0.35 * Math.sin(t * 0.9 + s.fase); s.p.rotation.x = 0.5 * Math.sin(t * 0.6 + s.fase * 1.3); }
      map.triggerRepaint(); }
    requestAnimationFrame(steg); };
  requestAnimationFrame(steg);
}
window.__festival = () => anim ? { id: anim.a.id, navn: anim.a.navn, straler: anim.straler.length } : null;
window.__festivalDatoer = aar => ARR.map(a => ({ id: a.id, d: (datoer(a, aar) || []).map(x => x.toISOString()) }));
export { aktiv as festival };
