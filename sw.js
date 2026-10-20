const CACHE_NAME = 'pensamiento-complejo-v2';
const STATIC_ASSETS = [
  './',
  './index.html',
  './red.html',
  './uca.html',
  './complejidades-hub.html',
  './newsletter.html',
  './manifest.webmanifest',
  './manifest.json',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-maskable-512.png',
  './icons/apple-touch-icon.png',
  './icons/favicon-32.png',
  './icons/logo-base.png'
];

// Install: Cache essential assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS).catch((err) => {
        console.warn('PWA: algunos recursos no se pudieron precachear:', err);
      });
    }).then(() => self.skipWaiting())
  );
});

// Activate: Clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch: Network-First for HTML/API, Cache-First for static assets
self.addEventListener('fetch', (event) => {
  const req = event.request;
  const url = new URL(req.url);

  // Skip non-GET and cross-origin requests that are not CDN assets
  if (req.method !== 'GET') return;

  // HTML / Navigation requests: Network First, fallback to cache
  if (req.mode === 'navigate' || req.headers.get('accept')?.includes('text/html')) {
    event.respondWith(
      fetch(req)
        .then((networkRes) => {
          if (networkRes.status === 200) {
            const resClone = networkRes.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(req, resClone));
          }
          return networkRes;
        })
        .catch(() => {
          return caches.match(req).then((cachedRes) => {
            if (cachedRes) return cachedRes;
            return caches.match('./index.html');
          });
        })
    );
    return;
  }

  // Google Sheets GVIZ: Stale While Revalidate
  if (url.hostname.includes('docs.google.com') && url.pathname.includes('/gviz/tq')) {
    event.respondWith(
      caches.open(CACHE_NAME).then((cache) => {
        return cache.match(req).then((cachedRes) => {
          const fetchPromise = fetch(req).then((networkRes) => {
            if (networkRes.status === 200) {
              cache.put(req, networkRes.clone());
            }
            return networkRes;
          }).catch(() => cachedRes);
          return cachedRes || fetchPromise;
        });
      })
    );
    return;
  }

  // Static Assets (Images, Icons, Fonts, CSS, JS): Cache First, background update
  event.respondWith(
    caches.match(req).then((cachedRes) => {
      if (cachedRes) {
        // Background revalidation
        fetch(req).then((networkRes) => {
          if (networkRes.status === 200) {
            caches.open(CACHE_NAME).then((cache) => cache.put(req, networkRes));
          }
        }).catch(() => {/* offline silent */});
        return cachedRes;
      }
      return fetch(req).then((networkRes) => {
        if (networkRes.status === 200 && (url.origin === location.origin || url.hostname.includes('r2.dev') || url.hostname.includes('fonts.googleapis.com') || url.hostname.includes('fonts.gstatic.com'))) {
          const resClone = networkRes.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(req, resClone));
        }
        return networkRes;
      }).catch((err) => {
        console.warn('PWA: fetch falló:', req.url, err);
      });
    })
  );
});
