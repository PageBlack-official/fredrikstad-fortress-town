import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { FXAAShader } from 'three/addons/shaders/FXAAShader.js';

const TEX_VANN=__TEKSTUR('vann.png');
const texLoader=new THREE.TextureLoader();
// Penselstrøk: bakt fra The Intergalactic Liquid & Irregular Brushes (Illustrator CC-installfil, tegnebrett 1–3, 23 strøk). Kilde: 05 Grafisk design/Illustrator Brushes.
const TEX_PENSEL=__TEKSTUR('pensel.png');
const penselTex=texLoader.load(TEX_PENSEL, t=>{ t.wrapS=t.wrapT=THREE.RepeatWrapping; t.minFilter=THREE.LinearMipmapLinearFilter; t.magFilter=THREE.LinearFilter; t.needsUpdate=true; });
const DATA = JSON.parse(document.getElementById('bydata').textContent);
const INK = 0x3a2c26;
const renderer = new THREE.WebGLRenderer({antialias:true});
// pikselbudsjett: store skjermer (5K/4K) starter med færre piksler, så introen går jevnt; heves etter introen hvis maskinen har overskudd
// skjermen tegnes alltid skarpt (full pikseltetthet). Mens kartet beveger seg regnes 3D-bildet i lavere oppløsning,
// og når det står stille tegnes det på nytt i full kvalitet - slik kart-apper gjør det.
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
const PIX_BEVEG=3.0e6, PIX_STILLE=11e6;
let skalaBeveg=1, skalaStille=1;
function beregnSkala(){ const n=renderer.domElement.width*renderer.domElement.height; skalaBeveg=THREE.MathUtils.clamp(Math.sqrt(PIX_BEVEG/n),0.4,1); skalaStille=1; /* stillbilde alltid i full oppløsning */ }
renderer.setSize(innerWidth,innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap; // myk filtrering gjøres i skyggeMask()
renderer.outputColorSpace = THREE.SRGBColorSpace;
document.body.prepend(renderer.domElement);
renderer.domElement.addEventListener('webglcontextlost',e=>{ e.preventDefault(); if(!sessionStorage.getItem('gl-tapt')){ sessionStorage.setItem('gl-tapt','1'); location.reload(); } });

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xe2e1d6);

// Ortografisk kamera = plakatens isometri
let VIEW = 300;
const cam = new THREE.OrthographicCamera(-1,1,1,-1,-4000,4000);
function fit(){
  const a = innerWidth/innerHeight;
  const v = a < 1 ? VIEW*1.15 : VIEW*0.62;
  cam.left=-v*a/1; cam.right=v*a/1; cam.top=v; cam.bottom=-v;
  if (a<1){ cam.left=-v*a; cam.right=v*a; }
  cam.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);
  post.size();
}
addEventListener('resize',fit);
