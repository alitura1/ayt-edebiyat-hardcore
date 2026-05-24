// REV6 M9 — Service Worker
// Strateji: HTML/JS/CSS stale-while-revalidate, data JSON network-first, asset cache-first
const VERSION = 'v21-2026-05-24-fen';
const STATIC_CACHE = `static-${VERSION}`;
const DATA_CACHE = `data-${VERSION}`;
const ASSETS_CACHE = `assets-${VERSION}`;

const STATIC_URLS = [
  '/',
  '/index.html',
  '/styles.css',
  '/manifest.json',
  '/app.js',
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(STATIC_CACHE).then(c => c.addAll(STATIC_URLS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(k => k !== STATIC_CACHE && k !== DATA_CACHE && k !== ASSETS_CACHE)
          .map(k => caches.delete(k))
    )).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);
  // Sadece same-origin GET'leri cache'le
  if (e.request.method !== 'GET' || url.origin !== location.origin) return;

  // 1) /data/*.json -> network-first, cache fallback
  if (url.pathname.startsWith('/data/')) {
    e.respondWith(
      fetch(e.request).then(resp => {
        const clone = resp.clone();
        caches.open(DATA_CACHE).then(c => c.put(e.request, clone));
        return resp;
      }).catch(() => caches.match(e.request))
    );
    return;
  }

  // 2) /assets/* + /lib/* + /pages/* -> stale-while-revalidate
  if (url.pathname.startsWith('/assets/') || url.pathname.startsWith('/lib/') || url.pathname.startsWith('/pages/')) {
    e.respondWith(
      caches.open(ASSETS_CACHE).then(c => {
        return c.match(e.request).then(cached => {
          const fetchP = fetch(e.request).then(resp => {
            c.put(e.request, resp.clone());
            return resp;
          }).catch(() => cached);
          return cached || fetchP;
        });
      })
    );
    return;
  }

  // 3) HTML / app shell -> stale-while-revalidate
  e.respondWith(
    caches.open(STATIC_CACHE).then(c => {
      return c.match(e.request).then(cached => {
        const fetchP = fetch(e.request).then(resp => {
          c.put(e.request, resp.clone());
          return resp;
        }).catch(() => cached || caches.match('/index.html'));
        return cached || fetchP;
      });
    })
  );
});

// REV6 M10 — Push notification
self.addEventListener('push', (e) => {
  const data = e.data ? e.data.json() : {};
  const title = data.title || 'AYT Edebiyat';
  const options = {
    body: data.body || 'Soru çözmenin vakti geldi 🎯',
    icon: '/assets/icon-192.svg',
    badge: '/assets/icon-192.svg',
    tag: data.tag || 'reminder',
  };
  e.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', (e) => {
  e.notification.close();
  e.waitUntil(
    self.clients.matchAll({ type: 'window' }).then(clients => {
      const url = e.notification.data?.url || '/#/atis';
      for (const c of clients) {
        if ('focus' in c) return c.focus();
      }
      if (self.clients.openWindow) return self.clients.openWindow(url);
    })
  );
});
