const V="hy-7bdb5f45f0";
self.addEventListener("install",e=>{self.skipWaiting();});
self.addEventListener("activate",e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==V).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));});
self.addEventListener("fetch",e=>{const r=e.request; if(r.method!=="GET"||r.cache==="no-store"||r.headers.has("range")||/\.(mp4|mov|webm)(\?|$)/.test(r.url)) return;
  const nav=r.mode==="navigate"||r.url.endsWith(".html");
  const net=(nav?fetch(r.url,{cache:"no-cache",credentials:"same-origin"}):fetch(r)).then(res=>{ if(res.ok){const c=res.clone(); caches.open(V).then(ca=>ca.put(r,c));} return res; });
  if(nav){ e.respondWith(net.catch(()=>caches.match(r).then(m=>m||caches.match("./")))); }
  else { e.respondWith(caches.match(r).then(m=>m||net)); }
});