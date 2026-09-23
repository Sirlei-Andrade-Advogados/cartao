// Guarda a tela de contato para ela abrir sem internet.
const CACHE = "contato-v1";
const ARQUIVOS = ["./", "./index.html", "./icone.png"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(ARQUIVOS)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys()
    .then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
    .then(() => self.clients.claim()));
});

// cache primeiro: abre instantâneo e funciona offline; atualiza por trás
self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET") return;
  e.respondWith(
    caches.match(e.request).then((achou) => {
      const rede = fetch(e.request)
        .then((r) => {
          if (r && r.ok) caches.open(CACHE).then((c) => c.put(e.request, r.clone()));
          return r;
        })
        .catch(() => achou);
      return achou || rede;
    })
  );
});
