// ---- kamerabroen: MapLibre eier kameraet; three.js-kameraet settes fra kartets matrise hvert bilde ----
// Modellen er i meter (x øst, y opp, z = -nord). MapLibre regner i mercator (x øst, y sør, z opp), så
// modellmatrisen er: flytt til origo · skaler(s,-s,s) · roter 90° om x.  (Samme oppskrift som MapLibres three.js-eksempel.)
const _merc=maplibregl.MercatorCoordinate.fromLngLat([ORIGO.lon,ORIGO.lat],0);
const MODELL=new THREE.Matrix4().makeTranslation(_merc.x,_merc.y,_merc.z)
  .multiply(new THREE.Matrix4().makeScale(1/M_PER_MERC,-1/M_PER_MERC,1/M_PER_MERC))
  .multiply(new THREE.Matrix4().makeRotationAxis(new THREE.Vector3(1,0,0),Math.PI/2));
const _mvp=new THREE.Matrix4(), _full=new THREE.Matrix4(), _inv=new THREE.Matrix4(), _pn=new THREE.Vector3(), _pf=new THREE.Vector3(), _dir=new THREE.Vector3();
kam.senter=new THREE.Vector3(10,0,0); kam.oye=new THREE.Vector3();
function kameraFraKartet(args){
  _mvp.fromArray(args.defaultProjectionData.mainMatrix); _full.multiplyMatrices(_mvp,MODELL); _inv.copy(_full).invert();
  // øyet: nær- og fjernpunktet på midtstrålen gir synsretningen; øyet ligger nærplanavstanden bak nærpunktet
  _pn.set(0,0,-1).applyMatrix4(_inv); _pf.set(0,0,1).applyMatrix4(_inv); _dir.subVectors(_pf,_pn).normalize();
  kam.naer=args.nearZ; kam.fjern=args.farZ; kam.fov=args.fov;
  kam.zoomfaktor=Math.pow(2,map.getZoom()-Z_HJEM); kam.pitch=map.getPitch(); kam.bearing=map.getBearing();
  kam.mpp=40075016.686*Math.cos(ORIGO.lat*Math.PI/180)/(512*Math.pow(2,map.getZoom()));
  kam.oye.copy(_pn).addScaledVector(_dir,-args.nearZ*kam.mpp);   // nearZ er i kartets pikselrom; mpp gjør det om til meter
  cam.position.copy(kam.oye); cam.up.set(0,1,0); cam.lookAt(_pf); // sikter mot fjernplanet, aldri mot nærplanet: når nearZ er nær null faller øyet sammen med nærpunktet og retningen blir tilfeldig cam.updateMatrix(); cam.updateMatrixWorld(true); cam.matrixWorldInverse.copy(cam.matrixWorld).invert();
  cam.projectionMatrix.multiplyMatrices(_full,cam.matrixWorld); cam.projectionMatrixInverse.copy(cam.projectionMatrix).invert();
  // bakkepunktet midt i bildet, og meter per skjermpunkt der
  const t=-_pn.y/_dir.y; if(isFinite(t)&&t>0) kam.senter.copy(_pn).addScaledVector(_dir,t);
}
// synsvinkler slik resten av koden forventer dem (asimut fra bearing, polarvinkel fra pitch)
function vinkler(){ return {az:-kam.bearing*Math.PI/180, pol:kam.pitch*Math.PI/180}; }
// kartet får vite hvor byen ligger, så det ikke kan dras ut av syne
const GRENSE=560;
map.setMaxBounds([tilLngLat(-GRENSE-300,-GRENSE-300), tilLngLat(GRENSE+300,GRENSE+300)]);
