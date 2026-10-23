import * as THREE from 'three';
import * as maplibregl from 'maplibre-gl';
import { FXAAShader } from 'three/addons/shaders/FXAAShader.js';

const TEX_VANN=__TEKSTUR('vann.png');
const texLoader=new THREE.TextureLoader();
// Penselstrøk: bakt fra The Intergalactic Liquid & Irregular Brushes (Illustrator CC-installfil, tegnebrett 1–3, 23 strøk). Kilde: 05 Grafisk design/Illustrator Brushes.
const TEX_PENSEL=__TEKSTUR('pensel.png');
const penselTex=texLoader.load(TEX_PENSEL, t=>{ t.wrapS=t.wrapT=THREE.RepeatWrapping; t.minFilter=THREE.LinearMipmapLinearFilter; t.magFilter=THREE.LinearFilter; t.needsUpdate=true; });
const DATA = JSON.parse(document.getElementById('bydata').textContent);
const INK = 0x3a2c26;
// ---- kartmotoren: MapLibre GL JS eier kamera, gester, zoom og koordinater; byen tegnes som et custom layer i three.js ----
const Q0=new URLSearchParams(location.search);
const ORIGO={lon:10.952745, lat:59.202835};   // modellens (0,0) i grader (KILDER.md); x = øst, y = nord i meter
const M_PER_MERC=1/maplibregl.MercatorCoordinate.fromLngLat([ORIGO.lon,ORIGO.lat],0).meterInMercatorCoordinateUnits();
function tilLngLat(x,y){ const m=maplibregl.MercatorCoordinate.fromLngLat([ORIGO.lon,ORIGO.lat],0); const s=1/M_PER_MERC; return new maplibregl.MercatorCoordinate(m.x+x*s, m.y-y*s, 0).toLngLat(); }
function tilModell(ll){ const o=maplibregl.MercatorCoordinate.fromLngLat([ORIGO.lon,ORIGO.lat],0), m=maplibregl.MercatorCoordinate.fromLngLat(ll,0); return [(m.x-o.x)*M_PER_MERC, -(m.y-o.y)*M_PER_MERC]; }
// plakatvinkelen: samme utsnitt som den ortografiske v25 (VIEW 300 → 372 m synlig høyde ved zoom 1)
const PITCH0=90-33, AZ0_GRADER=innerWidth/innerHeight<0.8 ? 130 : 40;
function zoomFor(faktor){ const mpp=372/innerHeight/faktor; return Math.log2(40075016.686*Math.cos(ORIGO.lat*Math.PI/180)/(512*mpp)); }
const Z_HJEM=zoomFor(1);
const map = new maplibregl.Map({ container:'kart', style:{version:8, sources:{}, layers:[{id:'papir', type:'background', paint:{'background-color':'#e2e1d6'}}]},
  center: tilLngLat(10,0), zoom: Z_HJEM, bearing: -AZ0_GRADER, pitch: PITCH0, minZoom: zoomFor(0.85), maxZoom: zoomFor(6), maxPitch: 72, minPitch: 18,
  attributionControl:false, antialias:true, respectPrefersReducedMotion:false, pixelRatio: Math.min(devicePixelRatio,2), doubleClickZoom:true, dragRotate:true, touchPitch:true, fadeDuration:0, renderWorldCopies:false });
window.map=map;
map.scrollZoom.setWheelZoomRate(1/150); map.touchZoomRotate.enable(); map.dragRotate.enable(); map.keyboard.enable();
// pluss/minus og kompass (snu byen, nordvend): synlig vei til zoom og rotasjon for mus uten klyp
map.addControl(new maplibregl.NavigationControl({showZoom:true, showCompass:true, visualizePitch:true}), 'bottom-right');
const gl2 = map.getCanvas().getContext('webgl2');
const renderer = new THREE.WebGLRenderer({canvas: map.getCanvas(), context: gl2, antialias:true});
renderer.autoClear=false;
// én tegnekvalitet: bildet tegnes likt om kartet beveger seg eller står stille, så skygger og strek aldri hopper mellom grov og fin.
// Oppløsningen settes av skjermen (pikselbudsjett) og senkes én gang for godt på svake maskiner (maalYtelse), aldri per gest.
const PIX=11e6;
let skalaStille=1, skalaMaskin=1;   // skalaMaskin: 1 på vanlige maskiner, lavere når maalYtelse har målt at maskinen ikke holder følge
function beregnSkala(){ const n=renderer.domElement.width*renderer.domElement.height; skalaStille=THREE.MathUtils.clamp(Math.sqrt(PIX/n),0.5,1)*skalaMaskin; }
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
function fit(){ post.size(); }
map.on('resize',fit);
