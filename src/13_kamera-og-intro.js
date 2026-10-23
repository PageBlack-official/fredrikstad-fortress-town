// ---- kamera og intro ----
const target = new THREE.Vector3(10,0,0);
const R = 900, ELEV = THREE.MathUtils.degToRad(33);
const AZ0 = THREE.MathUtils.degToRad(innerWidth/innerHeight<0.8 ? 130 : 40); // plakatvinkelen; på stående mobil dreid 90° så byens lengde fyller skjermen
function place(az, el=ELEV){ cam.position.set(target.x+Math.cos(el)*Math.sin(az)*R, target.y+Math.sin(el)*R, target.z+Math.cos(el)*Math.cos(az)*R); cam.lookAt(target); }
// introen: starter høyt over byen og nærmere, senker seg til plakatens vinkel mens byen snurrer én gang
const EL0=THREE.MathUtils.degToRad(52), Z0=0.82, SVEIP=THREE.MathUtils.degToRad(110); // intro: rask sveip inn mot plakatvinkelen, litt zoom inn
fit(); place(AZ0); scene.add(cam); lysFraVenstre();
const Q0=new URLSearchParams(location.search);
const controls = new OrbitControls(cam, renderer.domElement);
controls.target.copy(target); controls.enableDamping=true; controls.dampingFactor=0.07; controls.rotateSpeed=0.65;
controls.minPolarAngle=THREE.MathUtils.degToRad(20); controls.maxPolarAngle=THREE.MathUtils.degToRad(72);
controls.minZoom=0.85; controls.maxZoom=6; controls.enablePan=true; controls.screenSpacePanning=false; controls.panSpeed=1.0;
controls.mouseButtons={LEFT:THREE.MOUSE.ROTATE, MIDDLE:THREE.MOUSE.PAN, RIGHT:THREE.MOUSE.PAN}; // dra = snu byen, høyreklikk/sveip = flytte kartet
controls.enableZoom=false;                      // zoom styres av kartet selv: myk, mot pekeren, klyp på mobil
controls.touches={ONE:THREE.TOUCH.ROTATE, TWO:-1};   // to fingre håndteres under (klyp, vri, flytt)
controls.enabled=false;

// byen tegner seg opp: høyden vokser kvartal for kvartal (sortert sørvest -> nordøst)
const order = buildings.map(g=>{const c=g.userData.b.r; return [g, c[0]+c[1]];}).sort((a,b)=>a[1]-b[1]);
order.forEach(([g],k)=>{ g.userData.delay = 1.1*k/order.length; g.scale.y=0.001; });
let vokst=false;   // husene og trærne har vokst ferdig
function vokse(t){
  let ferdig=true;
  buildings.forEach(g=>{ const k=THREE.MathUtils.clamp((t-g.userData.delay)/0.5,0,1); g.scale.y=Math.max(0.001, 1-Math.pow(1-k,3)); if(k<1) ferdig=false; });
  if(t<3.4){ setCrowns(t); ferdig=false; } else setCrowns(null);
  if(ferdig) vokst=true;
}
