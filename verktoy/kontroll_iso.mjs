// Kontrolløren (30.10): den ekte three.js-scenen (ut/enkel/index.html) tegnet i NØYAKTIG samme parallellprojeksjon som Vegars
// kvartaltegning, så modellen kan legges oppå tegningen piksel for piksel.
// Bruk: node verktoy/kontroll_iso.mjs ut/enkel/index.html <jobb.json> <utmappe>
// jobb.json (lages av verktoy/kontroll.py render): [{navn, W, H, R, A}] der A er 2x4: [x, y, z, 1] modellmeter -> tegningens
// PDF-punkt (y ned), og R rasterpiksler per punkt. For hver tegning skrives tre bilder i <utmappe>:
//   <navn>-farge.png  flate farger: tak og vegger som vender mot venstre i bildet får materialets farge («farge»), de andre
//                     skyggetonen («skygge»), som i tegningen; vinduer/dører mørke. Hvit bakgrunn.
//   <navn>-id.png     byggindeks + 1 i R*256+G (DATA.bygg-rekkefølgen, samme som aBygg), B = flatetype (1 vegg, 2 tak, 3 vindu/dør, 4 annet)
//   <navn>-normal.png verdensnormalen (0.5+0.5n) til strek fra normalsprang
//   <navn>-idalle.png som id, men med ALLE bygg (jobbens vis-liste gjelder ikke): hus modellen har der tegningen ikke har noe
// forsk (valgfri): {id: [dx, dy]} forskyvning i PDF-punkt per bygg (blokkens plass i frihåndstegningen).
// vis (valgfri): id-ene som tegnes i farge/id/normal (tegningens hus); uten vis tegnes alle.
// og <navn>-id.json: {indeks: id} for byggene i bildet.
// Bare bygg tegnes (alt i byen med byggindeks: vanlige hus, spesielle grupper som kirka og portbyggene, vinduene). Trær, bakke,
// vann, murer, broer, brygger, statuen og kontaktskyggen tegnes ikke. Kameraet: THREE.Camera med projeksjonsmatrisen satt direkte
// (verdensrom = modell x, høyde, -y; src/05_bygg.js), dybde langs synsretningen (nullrommet til A).
import pw from '/opt/npm-tools/node_modules/playwright/index.js'; const { chromium } = pw;
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const [,, file, jobbFil, utdir] = process.argv; const dir = path.dirname(file);
const jobb = JSON.parse(fs.readFileSync(jobbFil, 'utf8'));
const server = http.createServer((q, r) => { const u = q.url.split('?')[0]; const p = path.join(dir, u === '/' ? 'index.html' : u); if (fs.existsSync(p) && fs.statSync(p).isFile()) { r.setHeader('content-type', p.endsWith('.json') ? 'application/json' : p.endsWith('.js') ? 'text/javascript' : p.endsWith('.png') ? 'image/png' : 'text/html; charset=utf-8'); r.end(fs.readFileSync(p)); } else { r.statusCode = 404; r.end(); } });
await new Promise(r => server.listen(0, '127.0.0.1', r)); const port = server.address().port;
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const ctx = await browser.newContext({ viewport: { width: 900, height: 600 } }); const page = await ctx.newPage();
const errs = []; page.on('pageerror', e => errs.push(e.message)); page.on('console', m => { if (m.type() === 'error') errs.push('console: ' + m.text().slice(0, 200)); });
await page.goto(`http://127.0.0.1:${port}/index.html?skip=1`, { waitUntil: 'load' });
await page.waitForFunction(() => window.__scene && window.__vis, null, { timeout: 120000 });
await page.waitForTimeout(3000);
// husene i full høyde (introen hoppes over): __vis setter vekst 1 og løft 0 på alle bygg
await page.evaluate(() => window.__vis(20, 1, 0, 0));
await page.waitForTimeout(3000);
fs.mkdirSync(utdir, { recursive: true });
for (const j of jobb) {
  const t0 = Date.now();
  const res = await page.evaluate(async (j) => {
    const THREE = await import('three');
    const { city } = window.__scene();
    const DATA = JSON.parse(document.getElementById('bydata').textContent);
    const W = j.W, H = j.H, R = j.R, A = j.A;
    // modell (x, y, z) = verden (X, -Zw, Y): rad i verdensrommet
    const rad = a => [a[0], a[2], -a[1], a[3]];
    const U = rad(A[0]), V = rad(A[1]);
    // synsretning: n = A0 x A1 (modellrom), snudd så den peker opp (mot tegneren); nærmere = større n·p
    const a0 = A[0].slice(0, 3), a1 = A[1].slice(0, 3);
    let n = [a0[1] * a1[2] - a0[2] * a1[1], a0[2] * a1[0] - a0[0] * a1[2], a0[0] * a1[1] - a0[1] * a1[0]];
    const ln = Math.hypot(...n); n = n.map(v => v / ln); if (n[2] < 0) n = n.map(v => -v);
    const Nw = [n[0], n[2], -n[1]];
    const D = 4000;   // dybdeområde (m)
    const cam = new THREE.Camera();
    // NDC: x = 2uR/W - 1, y = 1 - 2vR/H, z = -(n·p)/D
    const m = new THREE.Matrix4().set(
      2 * R / W * U[0], 2 * R / W * U[1], 2 * R / W * U[2], 2 * R / W * U[3] - 1,
      -2 * R / H * V[0], -2 * R / H * V[1], -2 * R / H * V[2], -2 * R / H * V[3] + 1,
      -Nw[0] / D, -Nw[1] / D, -Nw[2] / D, 0,
      0, 0, 0, 1);
    cam.projectionMatrix.copy(m); cam.projectionMatrixInverse.copy(m).invert();
    cam.matrixWorld.identity(); cam.matrixWorldInverse.identity(); cam.matrixAutoUpdate = false; cam.matrixWorldAutoUpdate = false;
    const cv = document.createElement('canvas'); cv.width = W; cv.height = H;
    const ren = new THREE.WebGLRenderer({ canvas: cv, antialias: false, preserveDrawingBuffer: true, alpha: false });
    ren.setPixelRatio(1); ren.setSize(W, H, false); ren.outputColorSpace = THREE.LinearSRGBColorSpace; ren.setClearColor(0xffffff, 1);
    // hvilket bygg hvert nett tilhører: aBygg-attributtet, ellers nærmeste forelder med userData.i (spesielle grupper)
    const nett = [];
    (function gaa(o, i) { if (o.userData && Number.isInteger(o.userData.i)) i = o.userData.i; if (o.isMesh) nett.push([o, i]); o.children.forEach(c => gaa(c, i)); })(city, -1);
    // hvilke bygg som tegnes i fargepasset (tegningens hus); idalle-passet tar alle
    const vis = new Uint8Array(1024 * 4); const visSett = new Set(j.vis || []);
    DATA.bygg.forEach((b, i) => { if (!j.vis || visSett.has(b.id)) vis[(i + 1) * 4] = 255; });
    const tVis = new THREE.DataTexture(vis, 1024, 1, THREE.RGBAFormat); tVis.needsUpdate = true;
    const tAlle = new THREE.DataTexture(new Uint8Array(1024 * 4).fill(255), 1024, 1, THREE.RGBAFormat); tAlle.needsUpdate = true;
    // forskyvning per bygg (blokkens forskyvning i tegningen, pt -> piksler), lest i vertex-shaderen
    const off = new Float32Array(1024 * 4); const idx = {}; DATA.bygg.forEach((b, i) => { idx[b.id] = i + 1; });
    for (const [id, d] of Object.entries(j.forsk || {})) { const k = idx[id]; if (k) { off[k * 4] = d[0] * R; off[k * 4 + 1] = d[1] * R; } }
    const tOff = new THREE.DataTexture(off, 1024, 1, THREE.RGBAFormat, THREE.FloatType); tOff.needsUpdate = true;
    const VS = `attribute float aBygg; uniform float uId; uniform sampler2D tVis, tOff; uniform vec2 uWH; varying vec3 vw; varying float vId;
      #ifdef VIND
      attribute vec4 aInfo; varying vec4 vInfo; varying vec2 vM, vSz;
      #endif
      void main(){ vec4 p=vec4(position,1.);
      #ifdef VIND
      vInfo=aInfo; vSz=vec2(length(instanceMatrix[0].xyz),length(instanceMatrix[1].xyz)); vM=uv*vSz;
      #endif
      #ifdef USE_INSTANCING
      p=instanceMatrix*p;
      #endif
      vec4 w=modelMatrix*p; vw=w.xyz; vId = uId>0.5 ? uId : aBygg;
      vec2 tc=vec2((floor(vId+0.5)+0.5)/1024., 0.5);
      vec2 o=texture2D(tOff, tc).xy;
      if(texture2D(tVis, tc).r < 0.5) vId = 0.;
      gl_Position=projectionMatrix*viewMatrix*w; gl_Position.x += 2.*o.x/uWH.x; gl_Position.y -= 2.*o.y/uWH.y; }`;
    // vinduets form i alle passene, samme utsnitt som src/07 (30.10): rundbuevindu (typ 0, bue 1), port med buet topp (typ 2)
    // og oksøye (typ 3); før ble alle vinduer tegnet som rektangler i kontrollbildet, så rådhusets rundbuer så rette ut
    const FORM = `#ifdef VIND
      varying vec4 vInfo; varying vec2 vM, vSz;
      #define FORM() { float t_=vInfo.x, b_=vInfo.y; if(t_>2.5){ if(length(vM-vSz*0.5)>vSz.x*0.5) discard; } else if(t_>1.5 || (t_<0.5 && b_>0.5 && b_<1.5)){ float r_=vSz.x*0.5; float c_=vSz.y-r_; if(vM.y>c_ && length(vec2(vM.x-r_,vM.y-c_))>r_) discard; } }
      #else
      #define FORM()
      #endif
      `;
    const FS_FARGE = `${FORM}uniform vec3 farge, skygge; uniform vec3 rU; uniform float typ; varying vec3 vw; varying float vId;
      void main(){ if(vId<0.5) discard; FORM(); vec3 nn=normalize(cross(dFdx(vw),dFdy(vw)));
        vec3 c = farge;
        if(typ<1.5 && abs(nn.y)<0.3){ c = dot(rU,nn) < 0. ? farge : skygge; }
        if(typ>1.5 && typ<2.5 && nn.y<0.3){ c = dot(rU,nn) < 0. ? farge : skygge; }
        gl_FragColor=vec4(c,1.); }`;
    const FS_ID = `${FORM}uniform float typ; varying vec3 vw; varying float vId;
      void main(){ if(vId<0.5) discard; FORM(); float i=floor(vId+0.5); vec3 nn=normalize(cross(dFdx(vw),dFdy(vw)));
        float t = typ>2.5 ? typ : (abs(nn.y)<0.3 ? 1. : 2.);
        gl_FragColor=vec4(floor(i/256.)/255., mod(i,256.)/255., t/255., 1.); }`;
    const FS_N = `${FORM}varying vec3 vw; varying float vId; void main(){ if(vId<0.5) discard; FORM(); vec3 nn=normalize(cross(dFdx(vw),dFdy(vw))); gl_FragColor=vec4(0.5+0.5*nn,1.); }`;
    const rU = new THREE.Vector3(U[0], U[1], U[2]);
    const lager = new Map();
    function matFor(o, i, pass) {
      const om = o.material; const mm = Array.isArray(om) ? om[0] : om;
      let farge = new THREE.Color(0.8, 0.8, 0.8), skygge = null, typ = 0;
      if (mm.uniforms && mm.uniforms.farge) { farge = mm.uniforms.farge.value.clone(); skygge = mm.uniforms.skygge ? mm.uniforms.skygge.value.clone() : null; }
      else if (mm.color) farge = mm.color.clone();
      if (o.isInstancedMesh) { typ = 3; farge = new THREE.Color(0.22, 0.25, 0.30); }
      if (!skygge) { skygge = farge.clone(); skygge.r *= 0.72; skygge.g *= 0.8; skygge.b *= 0.8; }
      farge = farge.clone().convertLinearToSRGB(); skygge = skygge.clone().convertLinearToSRGB();   // materialene har lineære farger
      const fs = pass === 'farge' ? FS_FARGE : pass.startsWith('id') ? FS_ID : FS_N;
      const vind = o.isInstancedMesh && o.geometry.getAttribute('aInfo') ? { VIND: '' } : {};
      return new THREE.ShaderMaterial({ vertexShader: VS, fragmentShader: fs, side: THREE.DoubleSide, defines: vind,
        uniforms: { farge: { value: farge }, skygge: { value: skygge }, rU: { value: rU }, typ: { value: typ }, uId: { value: i >= 0 ? i + 1 : 0 }, tVis: { value: pass === 'idalle' ? tAlle : tVis }, tOff: { value: tOff }, uWH: { value: new THREE.Vector2(W, H) } } });
    }
    const gamle = nett.map(([o]) => [o, o.material, o.visible, o.renderOrder, o.frustumCulled]);
    // projeksjonsmatrisen er satt for hånd, så frustumtesten til three.js gjelder ikke: uten dette ble grupper med egne nett
    // (portbyggene, bygg med deler) kastet, og bare vinduene (frustumCulled false) kom med (30.10, natt/landemerker)
    nett.forEach(([o]) => { o.frustumCulled = false; });
    const ut = {};
    // tak over vegger når de deler piksler (takutstikk): bygg-id er det viktige, dybdetesten tar resten
    for (const pass of ['farge', 'id', 'normal', 'idalle']) {
      nett.forEach(([o, i]) => {
        const kontakt = o.material && o.material.blending === THREE.MultiplyBlending;
        o.visible = !kontakt; if (kontakt) return;
        o.material = matFor(o, i, pass);
      });
      ren.render(city, cam);
      ut[pass] = cv.toDataURL('image/png');
      nett.forEach(([o]) => { if (o.material && o.material.dispose && o.visible) o.material.dispose(); });
    }
    gamle.forEach(([o, m, v, r, fc]) => { o.material = m; o.visible = v; o.renderOrder = r; o.frustumCulled = fc; });
    ren.dispose();
    const ids = {}; DATA.bygg.forEach((b, i) => { ids[i + 1] = b.id; });
    return { ut, ids, n: nett.length };
  }, j);
  for (const [k, v] of Object.entries(res.ut)) fs.writeFileSync(path.join(utdir, `${j.navn}-${k}.png`), Buffer.from(v.split(',')[1], 'base64'));
  fs.writeFileSync(path.join(utdir, `${j.navn}-id.json`), JSON.stringify(res.ids));
  console.log('ok', j.navn, `${j.W}x${j.H}`, res.n, 'nett', ((Date.now() - t0) / 1000).toFixed(1) + 's');
}
if (errs.length) console.log('sidefeil:', errs.slice(0, 5));
await browser.close(); server.close();
