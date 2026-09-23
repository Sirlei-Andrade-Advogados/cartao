// Guarda a tela de contato para abrir sem internet.
// O nome "contato-v1" é o mesmo da tela da Dra. Sirlei, de propósito: o
// service worker dela (publicado, não muda) apaga no activate todo cache com
// outro nome. As entradas não colidem porque cada tela guarda as próprias
// URLs. Por isso este aqui também nunca apaga cache nenhum.
const CACHE = "contato-v1";
const ARQUIVOS = ["./", "./index.html", "./icone.png"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(ARQUIVOS)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(self.clients.claim());
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
