import { SENERE, TILSTAND } from './tilstand.js';
import { BERORING, map, tilModell } from './00_oppsett.js';
import { buildings } from './06_kirka-bygget-etter-2017.js';
import { GRENSE } from './13_kart.js';
// ---- lenka husker utsikten : #view=lat,lon,zoom,pitch,bearing&hus=<bygg-id> ----
// Hashen skrives med history.replaceState (ingen nye historikkinnslag) når kameraet har stoppet, og når siden skjules eller lukkes.
// En lenke med view= (eller hus=) hopper over introen og går rett dit; hus= løfter huset og åpner kortet som ved klikk.
// Ugyldige verdier ignoreres: tall som ikke er tall, et senter utenfor kartets ramme, et hus som ikke finnes. Zoom og vinkler klemmes
// innen kartets egne grenser. Inne i en sandbox (claude.ai-artefakten) kan history og localStorage mangle; da virker kartet uten dem.
const LENKE=(()=>{
  let h=''; try{ h=decodeURIComponent((location.hash||'').replace(/^#/,'')); }catch(e){ h=''; }
  const par={}; h.split('&').forEach(d=>{ const i=d.indexOf('='); if(i>0) par[d.slice(0,i).trim().toLowerCase()]=d.slice(i+1).trim(); });
  let vis=null;
  if(par.view){
    const v=par.view.split(',').map(s=>s.trim()==='' ? NaN : Number(s));
    if(v.length===5 && v.every(Number.isFinite) && Math.abs(v[0])<=85 && Math.abs(v[1])<=180){
      const [lat,lon,zoom,pitch,bearing]=v, m=tilModell([lon,lat]), g=GRENSE+300;
      if(Math.abs(m[0])<=g && Math.abs(m[1])<=g){
        const klem=(x,a,b)=>Math.min(b,Math.max(a,x));
        vis={center:[lon,lat], zoom:klem(zoom,map.getMinZoom(),map.getMaxZoom()), pitch:klem(pitch,map.getMinPitch(),map.getMaxPitch()), bearing:((bearing%360)+540)%360-180};
      }
    }
  }
  const husId=/^[a-z]+-[0-9a-z]+$/i.test(par.hus||'') ? par.hus : null;
  const hus=husId ? buildings.find(g=>g.userData.b && g.userData.b.id===husId && !g.userData.b.skjul) || null : null;
  return {vis, hus, hopp: !!(vis||hus)};
})();
const LAGRET_UTSIKT='smart-old-town:utsikt';
function lenkeHash(){
  const c=map.getCenter(), f=(x,n)=>(+x.toFixed(n)).toString();
  let s=`view=${f(c.lat,5)},${f(c.lng,5)},${f(map.getZoom(),2)},${f(map.getPitch(),0)},${f(map.getBearing(),0)}`;
  if(SENERE.valgt && SENERE.valgt.userData.b && SENERE.valgt.userData.b.id) s+=`&hus=${SENERE.valgt.userData.b.id}`;
  return s;
}
function lenkeUrl(){ let base=''; try{ base=location.href.split('#')[0]; }catch(e){ base=''; } return base+'#'+lenkeHash(); }
// skrives bare når introen er ferdig (lenka til en halvferdig intro er ingen utsikt)
function lenkeSkriv(){
  if(!TILSTAND.introDone) return;
  const s='#'+lenkeHash();
  try{ if(location.hash!==s) window.history.replaceState(window.history.state, '', s); }catch(e){ /* sandbox uten historikk: kartet virker likevel */ }
  try{ window.localStorage.setItem(LAGRET_UTSIKT, s.slice(1)); }catch(e){ /* sandbox uten lagring */ }
}
// moveend: ett bilde etter, så introens egen moveend (som setter introDone) har kjørt først
map.on('moveend', ()=>setTimeout(lenkeSkriv, 0));
addEventListener('pagehide', lenkeSkriv);
document.addEventListener('visibilitychange', ()=>{ if(document.visibilityState==='hidden') lenkeSkriv(); });
// nettleserens tilbake lukker kortet (16_interaksjon); etterpå står innslaget fra før kortet, så utsikten skrives på nytt uten hus=
addEventListener('popstate', ()=>setTimeout(lenkeSkriv, 0));
// ved oppstart (15_loop, map.on('load')): kameraet rett til utsikten, så huset som ved klikk
function lenkeStart(){
  if(LENKE.vis) map.jumpTo(LENKE.vis);
  if(LENKE.hus) requestAnimationFrame(()=>{ SENERE.velgHus(LENKE.hus); lenkeSkriv(); });
  else lenkeSkriv();
}
// «Del» i huskortet: delingsarket på mobil (navigator.share), ellers utklippstavla; haken i knappen er bekreftelsen
async function lenkeDel(knapp){
  const url=lenkeUrl();
  const ok=()=>{ knapp.classList.add('delt'); clearTimeout(knapp._t); knapp._t=setTimeout(()=>knapp.classList.remove('delt'), 1600); };
  if(BERORING && navigator.share){
    try{ await navigator.share({url, title: document.title}); return; }
    catch(e){ if(e && e.name==='AbortError') return; }
  }
  try{ await navigator.clipboard.writeText(url); ok(); return; }catch(e){ /* utklippstavla stengt (sandbox): prøv den gamle veien */ }
  try{ const t=document.createElement('textarea'); t.value=url; t.setAttribute('readonly',''); t.style.cssText='position:fixed;left:-9999px;top:0;opacity:0';
    document.body.appendChild(t); t.select(); const lyktes=document.execCommand('copy'); t.remove(); if(lyktes) ok(); }catch(e){ /* ingen utklippstavle */ }
}
{ const knapp=document.querySelector('#kort .del'); if(knapp) knapp.addEventListener('click', ()=>lenkeDel(knapp)); }

export { LENKE, lenkeSkriv, lenkeStart };
