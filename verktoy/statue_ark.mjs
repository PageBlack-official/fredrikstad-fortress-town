// Kontrollark for statuen: tegner src/20_statuen-paa-torvet.js alene (samme kode, samme data/statue.json) fra fire vinkler,
// med målestokk (1 m-rutenett) og de målte høydene fra dataene som streker ved siden av. Ingen fremmede bilder.
// Bruk: node verktoy/statue_ark.mjs [ut.png]   (standard rapport/torvet/statue.png)
// Materialet er en flat to-tone-erstatning for kartets mat() (lys side / skyggeside), så arket viser form og proporsjon;
// fargene er de samme RGB-verdiene som i kartet.
import pw from '/opt/npm-tools/node_modules/playwright/index.js'; const { chromium } = pw;
import fs from 'node:fs'; import path from 'node:path'; import { fileURLToPath } from 'node:url';
const ROT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const ut = process.argv[2] || path.join(ROT, 'rapport', 'torvet', 'statue.png');
const kode = fs.readFileSync(path.join(ROT, 'src', '20_statuen-paa-torvet.js'), 'utf8');
const data = JSON.parse(fs.readFileSync(path.join(ROT, 'data', 'statue.json'), 'utf8'));
const im = JSON.parse(fs.readFileSync(path.join(ROT, 'src', 'importmap.json'), 'utf8'));
const html = `<!doctype html><meta charset="utf-8"><script type="importmap">${JSON.stringify(im)}</script>
<body style="margin:0;background:#f4f1ea"><script type="module">
import * as THREE from 'three';
window.THREE=THREE;
const DATA={statue:${JSON.stringify(data)}};
const city=new THREE.Group();
const LYS=new THREE.Vector3(-0.55,0.75,0.35).normalize();
const mats=new Map();
function mat(rgb,dim,sk){ const k=rgb.join()+'|'+(sk||[]).join(); if(!mats.has(k)){ const c=new THREE.Color(\`rgb(\${rgb})\`), s=sk?new THREE.Color(\`rgb(\${sk})\`):c.clone().multiplyScalar(0.75);
  mats.set(k,new THREE.ShaderMaterial({uniforms:{c:{value:c},s:{value:s},l:{value:LYS}},
  vertexShader:'varying vec3 wp; void main(){ vec4 w=modelMatrix*vec4(position,1.); wp=w.xyz; gl_Position=projectionMatrix*viewMatrix*w; }',
  fragmentShader:'uniform vec3 c,s,l; varying vec3 wp; void main(){ vec3 n=normalize(cross(dFdx(wp),dFdy(wp))); float d=dot(n,l); gl_FragColor=vec4(mix(s,c,smoothstep(-0.1,0.45,d)),1.); }'})); }
  return mats.get(k); }
function flatGruppe(g){ return g; }
${kode}
const scene=new THREE.Scene(); scene.background=new THREE.Color(0xf4f1ea);
const st=DATA.statue[0]; const grp=city.children[0];
// statuen tilbake til origo og uten dreiing, så vinklene er relative til fronten
grp.position.set(0,0,0); grp.rotation.set(0,0,0); scene.add(grp);
// 1 m-rutenett i bakken og en 5 m målestav
const gm=new THREE.LineBasicMaterial({color:0xb8b2a4});
for(let i=-3;i<=3;i++){ for(const [a,b] of [[[i,0,-3],[i,0,3]],[[-3,0,i],[3,0,i]]]) scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(...a),new THREE.Vector3(...b)]),gm)); }
const W=520,H=760; const r=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true}); r.setSize(W,H); document.body.appendChild(r.domElement);
// edges (stikkstrek) som i kartets blekkpass: kanter tegnet mørkt
const kanter=new THREE.Group(); grp.updateMatrixWorld(true);
grp.traverse(o=>{ if(o.isMesh){ const e=new THREE.LineSegments(new THREE.EdgesGeometry(o.geometry,35),new THREE.LineBasicMaterial({color:0x2a2a2a})); o.matrixWorld.decompose(e.position,e.quaternion,e.scale); kanter.add(e); } });
scene.add(kanter);
const vis=[['front (mot vest-nordvest)',0,0],['hans venstre side',90,0],['bak',180,0],['skrå ovenfra, fra hans høyre',-45,40]];
const bilder=[];
for(const [navn,az,el] of vis){
  const cam=new THREE.OrthographicCamera(-1.75,1.75,2.75,-2.5,0.1,100);   // 5,25 m høyt utsnitt rundt y = 2,4: 1 m = H/5,25 px
  const a=az*Math.PI/180, e=el*Math.PI/180, R=20;
  cam.position.set(Math.sin(a)*Math.cos(e)*R, 2.4+Math.sin(e)*R, Math.cos(a)*Math.cos(e)*R); cam.lookAt(0,2.4,0);
  r.render(scene,cam); bilder.push([navn, r.domElement.toDataURL('image/png')]);
}
window.__ferdig={bilder, hoyde: (()=>{ const b=new THREE.Box3().setFromObject(grp); return [b.min.x,b.min.y,b.min.z,b.max.x,b.max.y,b.max.z]; })()};
</script>`;
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 560, height: 800 } });
const feil = []; page.on('pageerror', e => feil.push(e.message)); page.on('console', m => { if (m.type() === 'error') feil.push(m.text()); });
await page.setContent(html, { waitUntil: 'load' });
await page.waitForFunction(() => window.__ferdig, null, { timeout: 120000 }).catch(() => {});
const res = await page.evaluate(() => window.__ferdig);
await browser.close();
if (!res) { console.error('statuen ble ikke tegnet:', feil.join('\n')); process.exit(1); }
const tmp = ut.replace(/\.png$/, '');
res.bilder.forEach(([navn, url], i) => fs.writeFileSync(`${tmp}-${i}.png`, Buffer.from(url.split(',')[1], 'base64')));
fs.writeFileSync(`${tmp}-vinkler.json`, JSON.stringify({ vinkler: res.bilder.map(b => b[0]), boks: res.hoyde, feil }, null, 1));
console.log('vinkler', res.bilder.length, 'boks (m)', res.hoyde.map(v => v.toFixed(2)).join(' '), feil.length ? 'FEIL: ' + feil.join('; ') : '');
