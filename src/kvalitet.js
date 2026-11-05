import * as THREE from 'three';
import { SENERE, TILSTAND, registrer } from './tilstand.js';
import { PIX, Q0, renderer } from './00_oppsett.js';
import { sun } from './02_lys.js';
// Kvaliteten: denne modulen eier alle beslutninger om oppløsning, strek (ss), skyggelegging (ao) og trinn. Ingen andre filer skriver dem.
// Regelen: kvaliteten trappes aldri ned av seg selv (Vegar: «akkurat det jeg har ønsket», se CHANGELOG). Oppløsningen settes av pikselbudsjettet (PIX) og skjermen.
// ?adapt=1 slår ytelsesmåleren på (test), ?nivaa=1|2 tvinger et trinn, ?noadapt=1 er beholdt for gamle lenker.
export const KVAL = { skalaStille: 1, skalaMaskin: 1, ssStille: 4, aoStille: 14, nivaa: Q0.get('noadapt') ? 9 : 0, onsket: 0 };
const MAAL_PAA = !!Q0.get('adapt');
let perfN = 0, perfSum = 0;

// oppløsningen som andel av lerretet: pikselbudsjettet delt på lerretets piksler, aldri under 0,5, aldri over 1
export function beregnSkala(){ const n=renderer.domElement.width*renderer.domElement.height; KVAL.skalaStille=THREE.MathUtils.clamp(Math.sqrt(PIX/n),0.5,1)*KVAL.skalaMaskin; }

// måleren (bare med ?adapt=1): tid fra bilde til bilde i bevegelse; under 45 bilder/s ønsker den ett trinn ned
export function maalYtelse(){ const n=performance.now(); if(!MAAL_PAA || KVAL.nivaa>=2 || document.hidden || !TILSTAND.introDone || !SENERE.vokst || (n-TILSTAND.sistBeveg>300 && n-TILSTAND.sistTegnet>40)) return;
  const dt=(window.__ramme||0)+(window.__mellom||0);
  perfN++; if(perfN>15){ perfSum+=dt; if(perfN>=75){ const avg=perfSum/60; perfN=0; perfSum=0; if(avg>22) KVAL.onsket=Math.max(KVAL.onsket, KVAL.nivaa+1); } } }

// trinnene: 1 = strek med to prøver og 80 % oppløsning; 2 = én prøve, 60 %, mindre skyggekart (telefon som sliter)
export function settNivaa(n){ KVAL.nivaa=n;
  if(n===1){ KVAL.ssStille=2; KVAL.skalaMaskin=0.8; }
  else if(n>=2){ KVAL.ssStille=1; KVAL.skalaMaskin=0.6; KVAL.aoStille=8; sun.shadow.mapSize.set(1024,1024); if(sun.shadow.map) sun.shadow.map.setSize(1024,1024); TILSTAND.skyggeSkitten=true; }   // setSize beholder teksturobjektet (dispose ga skyggekart uten skygger på mobil)
  beregnSkala(); }

// et ønsket trinn tas bare i bruk når kartet står, så bildet aldri bytter utseende midt i en gest
export function byttNivaaNaarStille(stille, fingerNede){ if(KVAL.onsket>KVAL.nivaa && stille && !fingerNede) settNivaa(KVAL.onsket); }

// feilsøkingsruta (?d=1): s bytter strek 4/2/1, a bytter skyggelegging 14/7/0, x bytter oppløsning 1/0,75
export function feilsokTast(t){
  if(t==='s') KVAL.ssStille = KVAL.ssStille===4 ? 2 : KVAL.ssStille===2 ? 1 : 4;
  if(t==='a') KVAL.aoStille = KVAL.aoStille===14 ? 7 : KVAL.aoStille===7 ? 0 : 14;
  if(t==='x') KVAL.skalaStille = KVAL.skalaStille===1 ? 0.75 : 1; }

if(Q0.get('nivaa')) settNivaa(+Q0.get('nivaa'));
registrer({ beregnSkala: () => beregnSkala });   // brukes av tidligere moduler via SENERE (tilstand.js)
