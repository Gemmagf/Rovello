/* Rovello service worker — instal·labilitat + memòria cau de l'app shell.
 * Estratègia:
 *  - Navegació (index.html): XARXA primer, memòria cau només si no hi ha xarxa
 *    (així una nova versió publicada es veu immediatament).
 *  - /static/ (fitxers amb hash al nom): memòria cau primer (immutables).
 *  - icones i manifest: memòria cau amb revalidació.
 *  - Mai es cachegen peticions a altres orígens (API, iNaturalist, OSM).
 */
const VERSION = 'rovello-v1';
const SHELL = `${VERSION}-shell`;
const STATIC = `${VERSION}-static`;
const BASE = new URL(self.registration.scope).pathname; // "/Rovello/"

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(SHELL).then((c) => c.addAll([BASE, `${BASE}manifest.json`]).catch(() => null))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(
      keys.filter((k) => !k.startsWith(VERSION)).map((k) => caches.delete(k))
    )).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return; // API i tercers: sempre xarxa

  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request)
        .then((res) => { caches.open(SHELL).then((c) => c.put(BASE, res.clone())); return res; })
        .catch(() => caches.match(BASE))
    );
    return;
  }
  if (url.pathname.startsWith(`${BASE}static/`)) {
    event.respondWith(
      caches.match(request).then((hit) => hit || fetch(request).then((res) => {
        if (res.ok) caches.open(STATIC).then((c) => c.put(request, res.clone()));
        return res;
      }))
    );
    return;
  }
  if (url.pathname.startsWith(`${BASE}icons/`) || url.pathname.endsWith('manifest.json') || url.pathname.endsWith('favicon.ico')) {
    event.respondWith(
      caches.open(SHELL).then(async (c) => {
        const hit = await c.match(request);
        const net = fetch(request).then((res) => { if (res.ok) c.put(request, res.clone()); return res; }).catch(() => null);
        return hit || (await net) || Response.error();
      })
    );
  }
});
