import * as THREE from 'three';
import * as maplibregl from 'maplibre-gl';
import { FXAAShader } from 'three/addons/shaders/FXAAShader.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

const TEX_VANN=__TEKSTUR('vann.png');
const texLoader=new THREE.TextureLoader();
// Penselstrøk: bakt fra The Intergalactic Liquid & Irregular Brushes (Illustrator CC-installfil, tegnebrett 1–3, 23 strøk). Kilde: 05 Grafisk design/Illustrator Brushes.
const TEX_PENSEL=__TEKSTUR('pensel.png');
const penselTex=texLoader.load(TEX_PENSEL, t=>{ t.wrapS=t.wrapT=THREE.RepeatWrapping; t.minFilter=THREE.LinearMipmapLinearFilter; t.magFilter=THREE.LinearFilter; t.needsUpdate=true; });
const DATA = JSON.parse(document.getElementById('bydata').textContent);
const INK = 0x3a2c26;
// ---- kartmotoren: MapLibre GL JS eier kamera, gester, zoom og koordinater; byen tegnes som et custom layer i three.js ----
const Q0=new URLSearchParams(location.search);
// ---- tegnestil (bestemt med Vegar): streken er stikkets, flatene er flate, lyset er glatt. 2015-teknikkens varme (akvarellvask,
// penselbrudd, papirkorn, vignett, skyskygger, løvflekker) er av. ?stil=c viser den gamle til sammenligning, ?stil=b legger skravur i skyggene.
const STIL=(()=>{ const v=Q0.get('stil')||'a';
  // kurve: filmkurven over høylysene (lys-og-bevegelse pkt. 1), avslått i kartet.
  const a={vask:0, pensel:0, korn:0, vignett:0, sky:0, stoy:0, skravur:0, kurve: Q0.get('kurve')==='1' ? 1 : 0};   // av i kartet (ingen synlig forskjell); ?kurve=1 for introfilmen
  if(v==='b') return {...a, skravur:1};
  if(v==='c') return {vask:1, pensel:1, korn:1, vignett:1, sky:1, stoy:1, skravur:0, kurve:0};
  return a; })();
// sola står fast i byen (modell), ikke i øyet (plakat): hjemmevisningen er lik trykket, og skyggene snur seg med byen. ?sol=plakat gir den gamle.
const SOL_FAST = Q0.get('sol')!=='plakat';
const ORIGO={lon:10.952745, lat:59.202835};   // modellens (0,0) i grader (KILDER.md); x = øst, y = nord i meter
const M_PER_MERC=1/maplibregl.MercatorCoordinate.fromLngLat([ORIGO.lon,ORIGO.lat],0).meterInMercatorCoordinateUnits();
function tilLngLat(x,y){ const m=maplibregl.MercatorCoordinate.fromLngLat([ORIGO.lon,ORIGO.lat],0); const s=1/M_PER_MERC; return new maplibregl.MercatorCoordinate(m.x+x*s, m.y-y*s, 0).toLngLat(); }
function tilModell(ll){ const o=maplibregl.MercatorCoordinate.fromLngLat([ORIGO.lon,ORIGO.lat],0), m=maplibregl.MercatorCoordinate.fromLngLat(ll,0); return [(m.x-o.x)*M_PER_MERC, -(m.y-o.y)*M_PER_MERC]; }
// plakatvinkelen: samme utsnitt som den ortografiske v25 (VIEW 300 → 372 m synlig høyde ved zoom 1)
// hjemmevisningen (Vegar: «sluttbildet i dette utsnittet»): byen sett fra elva, kirka oppe til høyre, litt brattere enn plakaten.
// Før: plakatvinkelen (asimut 40/130, høyde 33°). ?hjem=plakat gir den gamle.
const HJEM_PLAKAT=Q0.get('hjem')==='plakat';
// stående telefon har sitt eget sluttbilde (skjermbilde fra iPhone: «Uansett versjon vil jeg at denne stillingen skal være siste frame på mobilvisningen»):
// Torvet med statuen midt i bildet, Det gamle rådhus bak, kirka oppe til høyre, Vollgraven øverst, elva nederst. Asimut 193, faktor 1,22, sentrum MOBIL_START (14_speilinger), høyde 40°.
// Faktoren er relativ til skjermhøyden (zoomFor), så utsnittet blir det samme på alle telefoner. Endres bare etter ny dom fra Vegar; regel 35 vokter den.
const STAAENDE=innerWidth/innerHeight<0.8;
// hjemmevisningens høyde over horisonten: 48° på bred skjerm; 40° på smal (stående telefon), der 48° leses som «for mye ovenfra» (Vegar)
const PITCH0=90-(HJEM_PLAKAT?33:+(Q0.get('hoyde')||(innerWidth/innerHeight<0.8 ? 40 : 48))), AZ0_GRADER=HJEM_PLAKAT ? (innerWidth/innerHeight<0.8 ? 130 : 40) : +(Q0.get('az0')||(STAAENDE ? 193 : 200));
function zoomFor(faktor){ const mpp=372/innerHeight/faktor; return Math.log2(40075016.686*Math.cos(ORIGO.lat*Math.PI/180)/(512*mpp)); }
const Z_HJEM=zoomFor(HJEM_PLAKAT?1:+(Q0.get('z0')||(STAAENDE ? 1.22 : 1.3)));
const map = new maplibregl.Map({ container:'kart', style:{version:8, sources:{}, layers:[{id:'papir', type:'background', paint:{'background-color':'#e2e1d6'}}]},
  center: tilLngLat(10,0), zoom: Z_HJEM, bearing: -AZ0_GRADER, pitch: PITCH0, minZoom: zoomFor(0.85), maxZoom: zoomFor(6), maxPitch: 72, minPitch: 18,
  attributionControl:false, antialias:false /* lerretet får ingen MSAA: byen tegnes kantutjevnet i eget mål (01: MSAA + FXAA) og legges over hele lerretet, så MSAA på lerretet var dobbeltarbeid */, reduceMotion:false /* «Reduser bevegelse» av: Vegars valg, CHANGELOG v27 (15_bevegelse) */, pixelRatio: Math.min(devicePixelRatio,2), doubleClickZoom:true, dragRotate:true, touchPitch:true, fadeDuration:0, renderWorldCopies:false });
window.map=map;
map.scrollZoom.setWheelZoomRate(1/150); map.touchZoomRotate.enable(); map.dragRotate.enable(); map.keyboard.enable();
// pluss/minus og kompass (snu byen, nordvend): synlig vei til zoom og rotasjon for mus uten klyp
map.addControl(new maplibregl.NavigationControl({showZoom:true, showCompass:true, visualizePitch:true}), 'bottom-right');
const gl2 = map.getCanvas().getContext('webgl2');
const renderer = new THREE.WebGLRenderer({canvas: map.getCanvas(), context: gl2, antialias:true});
renderer.autoClear=false;
// én tegnekvalitet: bildet tegnes likt om kartet beveger seg eller står stille, så skygger og strek aldri hopper mellom grov og fin.
// Oppløsningen settes av skjermen (pikselbudsjett) og senkes én gang for godt på svake maskiner (maalYtelse), aldri per gest.
// pikselbudsjett per bilde: 11 M på en maskin, 5 M på berøringsskjerm (telefon/nettbrett tegner på DPR 2–3 og hang etter fingeren,
// Vegar; ytelsesmåleren trappet først ned etter 75 trege bilder). ?pix=<millioner> overstyrer.
const BERORING = window.matchMedia('(pointer: coarse)').matches;
const PIX=Q0.get('pix') ? +Q0.get('pix')*1e6 : (BERORING ? 5e6 : 11e6);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap; // myk filtrering gjøres i skyggeMask()
renderer.outputColorSpace = THREE.SRGBColorSpace;
map.on('webglcontextlost',()=>{ if(!sessionStorage.getItem('gl-tapt')){ sessionStorage.setItem('gl-tapt','1'); location.reload(); } });

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xe2e1d6);

// kameraet: posisjon og retning hentes fra MapLibre hvert bilde (se 13_kart.js); projeksjonen er kartets egen
const cam = new THREE.PerspectiveCamera(60, 1, 1, 10000);
cam.matrixAutoUpdate=false;
const kam={zoomfaktor:1, mpp:1, pitch:PITCH0, bearing:-AZ0_GRADER, naer:1, fjern:10000};   // avledet av kartet hvert bilde

export { AZ0_GRADER, BERORING, DATA, HJEM_PLAKAT, INK, M_PER_MERC, ORIGO, PITCH0, PIX, Q0, SOL_FAST, STAAENDE, STIL, TEX_VANN, Z_HJEM, cam, gl2, kam, map, penselTex, renderer, scene, texLoader, tilLngLat, tilModell, zoomFor };
