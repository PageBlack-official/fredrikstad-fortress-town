// Bilde-likhet for synsrand-kuttingen (PAG-1503): rendrer samme kamera med frustum-kutting PÅ (standard) og AV (?synsrand=0) og
// teller pikselforskjellen. Kutting skal bare fjerne nett som er HELT utenfor synsranden, så bildet må være identisk. Lite vindu +
// SwiftShader (rask, programvare — ingen konkurranse med Metal fra andre økter); likheten er uavhengig av oppløsning.
// Bruk: node verktoy/synsrand_parity.mjs ut/enkel/index.html rapport/_mobil_1503/parity.json
import { chromium } from './pw.mjs';
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path';
const [,, file, utfil] = process.argv; const dir = path.dirname(path.resolve(file));
const srv = http.createServer((q,r)=>{ const p=path.join(dir, q.url.split('?')[0]==='/'?'index.html':q.url.split('?')[0]); if(fs.existsSync(p)&&fs.statSync(p).isFile()){ r.setHeader('content-type','text/html;charset=utf-8'); r.end(fs.readFileSync(p)); } else {r.statusCode=404;r.end();} });
await new Promise(r=>srv.listen(0,'127.0.0.1',r)); const port=srv.address().port;
const b = await chromium.launch({ args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'] });
const W=520,H=520,DPR=1;
async function shot(ekstra, view){
  const ctx=await b.newContext({viewport:{width:W,height:H},deviceScaleFactor:DPR,isMobile:true,hasTouch:true});
  const page=await ctx.newPage(); page.on('pageerror',e=>console.log('ERR',e.message));
  await page.goto(`http://127.0.0.1:${port}/index.html?skip=1${ekstra}`,{waitUntil:'load'});
  await page.waitForFunction(()=>window.__kam&&window.__vaareBilder>3,null,{timeout:120000});
  await page.evaluate(v=>window.__vis(...v), view);
  const t0=Date.now(); while(Date.now()-t0<30000){ await page.waitForTimeout(300); const k=await page.evaluate(()=>window.__kam()); if(Math.abs(k.zoom-view[1])<0.02 && !k.anim) break; }
  await page.waitForTimeout(800);
  const png = await page.screenshot({ timeout: 60000 }); await ctx.close(); return png;
}
async function diff(a, b2){
  const ctx=await b.newContext(); const page=await ctx.newPage();
  const r = await page.evaluate(async ([aB,bB])=>{
    const dec = async arr=>{ const bmp=await createImageBitmap(new Blob([new Uint8Array(arr)])); const c=new OffscreenCanvas(bmp.width,bmp.height); const g=c.getContext('2d'); g.drawImage(bmp,0,0); return {d:g.getImageData(0,0,bmp.width,bmp.height).data,w:bmp.width,h:bmp.height}; };
    const A=await dec(aB), B=await dec(bB); if(A.w!==B.w||A.h!==B.h) return {feil:'ulik størrelse'};
    let maks=0, over8=0, over30=0, n=A.d.length/4; for(let i=0;i<A.d.length;i+=4){ const m=Math.max(Math.abs(A.d[i]-B.d[i]),Math.abs(A.d[i+1]-B.d[i+1]),Math.abs(A.d[i+2]-B.d[i+2])); if(m>maks)maks=m; if(m>8)over8++; if(m>30)over30++; }
    return {w:A.w,h:A.h,piksler:n,maksAvvik:maks,over8,over30,pst8:+(100*over8/n).toFixed(4),pst30:+(100*over30/n).toFixed(4)};
  }, [Array.from(a), Array.from(b2)]);
  await ctx.close(); return r;
}
const ut={ vindu:{W,H,DPR}, syn:{} };
for(const [navn,view] of [['zoom5',[200,5,60,60]],['zoom4-innerby',[200,4,40,-20]],['hjem',[200,1.3,25,25]]]){
  const paa=await shot('', view), av=await shot('&synsrand=0', view);
  ut.syn[navn]=await diff(paa,av); console.log(navn, JSON.stringify(ut.syn[navn]));
}
fs.mkdirSync(path.dirname(utfil),{recursive:true}); fs.writeFileSync(utfil, JSON.stringify(ut,null,1));
await b.close(); srv.close();
