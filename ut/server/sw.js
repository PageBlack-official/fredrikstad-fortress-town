// Tjenestearbeider: kartet virker uten nett etter første besøk. Versjonen i navnet byttes av bygg.py, så ny versjon rydder gammel buffer.
const NAVN='gamlebyen-33-92f7a1cf';
const FILER=['./','index.html','data/by.json','assets/vann.png','assets/pensel.png',
 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js',
 'https://cdn.jsdelivr.net/npm/maplibre-gl@6.14.0/dist/maplibre-gl.mjs','https://cdn.jsdelivr.net/npm/maplibre-gl@6.14.0/dist/maplibre-gl-shared.mjs','https://cdn.jsdelivr.net/npm/maplibre-gl@6.14.0/dist/maplibre-gl-worker.mjs',
 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/shaders/FXAAShader.js'];
self.addEventListener('install',e=>{ e.waitUntil(caches.open(NAVN).then(c=>c.addAll(FILER)).then(()=>self.skipWaiting())); });
self.addEventListener('activate',e=>{ e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==NAVN).map(k=>caches.delete(k)))).then(()=>self.clients.claim())); });
self.addEventListener('fetch',e=>{ e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request))); });
