// Omleggingen 05.11, steg 2: gjør de sammenlimte seksjonene om til ekte ES-moduler: hver fil importerer det den bruker og eksporterer det andre bruker.
const path=require('path'); const R_=path.join(__dirname,'..','..','node_modules')+'/'; process.chdir(path.join(__dirname,'..','..'));
const espree=require(R_+'espree'), scope=require(R_+'eslint-scope'), fs=require('fs');
const ORDEN=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const RN=['skyggeSkitten','introDone','_synlig','speilInn','speilFrisk','sistBeveg','sistTegnet','fullTegnet'];
const KN={skalaStille:'skalaStille',skalaMaskin:'skalaMaskin',ssStille:'ssStille',aoStille:'aoStille',perfNivaa:'nivaa',perfOnsket:'onsket'};
function analyser(tekster){
  let src='', spans=[];
  for(const f of ORDEN){ const s=tekster[f]; spans.push([src.length, src.length+s.length, f]); src+=s+'\n'; }
  const fileAt=p=>spans.find(([a,b])=>p>=a&&p<b);
  const ast=espree.parse(src,{ecmaVersion:'latest',sourceType:'module',range:true});
  const sm=scope.analyze(ast,{ecmaVersion:2022,sourceType:'module'});
  return {src,spans,fileAt,ast,sm};
}
let tekster={}; for(const f of ORDEN) tekster[f]=fs.readFileSync('src/'+f,'utf8');
// 1) R./K.-omskriving av gjennomgående navn
{ const {fileAt,ast,sm}=analyser(tekster);
  const shorthand=new Set(); (function walk(n){ if(!n||typeof n.type!=='string') return; if(n.type==='Property'&&n.shorthand) shorthand.add(n.value.range[0]); for(const k in n){ const v=n[k]; if(Array.isArray(v)) v.forEach(walk); else if(v&&typeof v.type==='string') walk(v); } })(ast);
  const edits={};
  for(const r of sm.globalScope.through){ const nm=r.identifier.name; let ny=null;
    if(RN.includes(nm)) ny='TILSTAND.'+nm; else if(KN[nm]) ny='KVAL.'+KN[nm]; if(!ny) continue;
    const [a,,f]=fileAt(r.identifier.range[0]); const st=r.identifier.range[0]-a, en=r.identifier.range[1]-a;
    (edits[f]??=[]).push([st,en, shorthand.has(r.identifier.range[0]) ? nm+':'+ny : ny]); }
  for(const f in edits){ let s=tekster[f]; for(const [a,b,t] of edits[f].sort((x,y)=>y[0]-x[0])) s=s.slice(0,a)+t+s.slice(b); tekster[f]=s; }
  console.log('omskrevet R/K:',Object.fromEntries(Object.entries(edits).map(([f,e])=>[f,e.length])));
}
// 1b) referanser til navn eid av en SENERE modul blir L.navn (sen oppslag), og eieren registrerer en getter
const reg={};
{ const {fileAt,ast,sm}=analyser(tekster); const mod=sm.globalScope.childScopes[0];
  const shorthand=new Set(); (function walk(n){ if(!n||typeof n.type!=='string') return; if(n.type==='Property'&&n.shorthand) shorthand.add(n.value.range[0]); for(const k in n){ const v=n[k]; if(Array.isArray(v)) v.forEach(walk); else if(v&&typeof v.type==='string') walk(v); } })(ast);
  const edits={};
  for(const v of mod.variables){ const d=v.defs[0]; if(!d||d.type==='ImportBinding') continue; const owner=fileAt(d.name.range[0])[2];
    for(const r of v.references){ const [a,,f]=fileAt(r.identifier.range[0]); if(f===owner || ORDEN.indexOf(owner)<ORDEN.indexOf(f)) continue;
      if(r.isWrite()) throw new Error('skriver senere navn '+v.name+' fra '+f);
      const st=r.identifier.range[0]-a, en=r.identifier.range[1]-a, nm=v.name;
      (edits[f]??=[]).push([st,en, shorthand.has(r.identifier.range[0]) ? nm+':SENERE.'+nm : 'SENERE.'+nm]); (reg[owner]??=new Set()).add(nm); } }
  for(const f in edits){ let s=tekster[f]; for(const [a,b,t] of edits[f].sort((x,y)=>y[0]-x[0])) s=s.slice(0,a)+t+s.slice(b); tekster[f]=s; }
  for(const f in reg) tekster[f]=tekster[f].replace(/\s*$/,'\n')+`registrer({ ${[...reg[f]].sort().map(n=>n+': () => '+n).join(', ')} });   // brukes av tidligere moduler via SENERE (tilstand.js)\n`;
  console.log('sene oppslag:',Object.fromEntries(Object.entries(reg).map(([f,v])=>[f,[...v]])));
}
// 2) importer/eksporter
const {fileAt,sm,ast}=analyser(tekster);
const mod=sm.globalScope.childScopes[0];
const imp={}, exp={}, bibl={};
for(const v of mod.variables){ const d=v.defs[0]; if(!d) continue; const owner=fileAt(d.name.range[0])[2];
  if(d.type==='ImportBinding'){ bibl[v.name]=d.parent; }
  for(const r of v.references){ const f=fileAt(r.identifier.range[0])[2]; if(f===owner) continue;
    if(d.type==='ImportBinding'){ (imp[f]??={}); (imp[f]['@'+v.name]=1); continue; }
    if(r.isWrite()) console.log('ADVARSEL skriver',v.name,'fra',f);
    ((imp[f]??={})[owner]??=new Set()).add(v.name); (exp[owner]??=new Set()).add(v.name); } }
const ubrukt=sm.globalScope.through.map(r=>r.identifier.name).filter(n=>!/^(__TEKSTUR)$/.test(n));
const src=ast; const srcText=analyser(tekster).src;
for(const f of ORDEN){ let hode=[];
  const i=imp[f]||{};
  for(const k of Object.keys(i).filter(k=>k[0]==='@')){ const nm=k.slice(1), dekl=bibl[nm]; const kilde=dekl.source.value;
    const spes=dekl.specifiers.find(s=>s.local.name===nm);
    hode.push(spes.type==='ImportNamespaceSpecifier' ? `import * as ${nm} from '${kilde}';` : `import { ${spes.imported.name===nm?nm:spes.imported.name+' as '+nm} } from '${kilde}';`); }
  for(const g of ORDEN){ if(i[g]) hode.push(`import { ${[...i[g]].sort().join(', ')} } from './${g}';`); }
  const fot = (exp[f] && !['tilstand.js','kvalitet.js'].includes(f)) ? `\nexport { ${[...exp[f]].sort().join(', ')} };\n` : '';
  fs.writeFileSync('src/'+f, (hode.length? hode.join('\n')+'\n':'') + tekster[f].replace(/\s*$/,'\n') + fot); }
fs.writeFileSync('src/main.js','// Inngangen: seksjonene lastes i denne rekkefølgen (bygg.py pakker dem til én fil med esbuild).\n'+ORDEN.map(f=>`import './${f}';`).join('\n')+'\n');
console.log('udefinerte globale som ikke er nettleserens:',[...new Set(ubrukt)].filter(n=>!(n in globalThis)&&!['document','location','innerWidth','innerHeight','devicePixelRatio','window','sessionStorage','performance','requestAnimationFrame','addEventListener','navigator','fetch','setTimeout','clearTimeout','setInterval','matchMedia','getComputedStyle','cancelAnimationFrame','history','alert','Image','localStorage','screen','scrollTo','visualViewport','removeEventListener','ResizeObserver','DOMParser','HTMLElement','Blob','URL','open','top','self','name','caches','dispatchEvent','CustomEvent','Event','PointerEvent','TouchEvent','KeyboardEvent','MouseEvent','WheelEvent'].includes(n)));
