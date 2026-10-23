import pw from '/opt/npm-tools/node_modules/playwright/index.js'; const { chromium } = pw;
const browser=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const page=await browser.newPage(); const errs=[]; page.on('pageerror',e=>errs.push(e.message)); page.on('console',m=>{ if(m.type()==='error') errs.push('console: '+m.text()); });
await page.goto('http://127.0.0.1:8765/index.html?skip=1'); await page.waitForTimeout(5000);
const ok=await page.evaluate(()=>typeof window.__vis==='function');
const sw=await page.evaluate(async()=>{ const r=await navigator.serviceWorker.getRegistration(); return !!r; });
console.log('kartet lastet:',ok,'tjenestearbeider registrert:',sw,'feil:',errs);
await browser.close();
