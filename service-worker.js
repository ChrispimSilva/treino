const CACHE_NAME = "treino-cache-v1";
const FILES_TO_CACHE = [
  "index.html",
  "manifest.json",
  "imagens/supino.jpg",
  "imagens/crucifixo.jpg",
  "imagens/peckdeck.jpg",
  "imagens/triceps_pulley.jpg",
  "imagens/triceps_inverso.jpg",
  "imagens/triceps_coice.jpg",
  "imagens/agachamento.jpg",
  "imagens/legpress.jpg",
  "imagens/extensora.jpg",
  "imagens/flexora.jpg",
  "imagens/puxada.jpg",
  "imagens/remada.jpg",
  "imagens/rosca.jpg",
  "imagens/elevacao_lateral.jpg",
  "imagens/icon-192.png",
  "imagens/icon-512.png"
];

// Instala e guarda arquivos
self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(FILES_TO_CACHE))
  );
});

// Ativa e remove caches antigos
self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.map(key => {
        if (key !== CACHE_NAME) {
          return caches.delete(key);
        }
      }))
    )
  );
});

// Intercepta requisições
self.addEventListener("fetch", event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});
