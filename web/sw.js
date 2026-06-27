const CACHE_NAME = 'vina-sanmartin-v1';
const ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/favicon-48.png',
  '/favicon-96.png',
  '/favicon-192.png',
  '/favicon-512.png',
  '/og-image.webp'
];

// Instalar y cachear recursos
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log('SW: Cacheando recursos...');
      return cache.addAll(ASSETS);
    })
  );
  self.skipWaiting();
});

// Activar y limpiar cachés viejas
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

// Estrategia: Network first, fallback a caché
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  event.respondWith(
    fetch(event.request)
      .then(response => {
        const clone = response.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        return response;
      })
      .catch(() => caches.match(event.request))
  );
});

// Notificaciones push
self.addEventListener('push', event => {
  const data = event.data ? event.data.json() : {};
  const title = data.title || '🍇 Viña San Martín';
  const options = {
    body: data.body || '¡Tenemos novedades para vos!',
    icon: '/favicon-192.png',
    badge: '/favicon-96.png',
    vibrate: [200, 100, 200],
    data: { url: data.url || '/' }
  };
  event.waitUntil(self.registration.showNotification(title, options));
});

// Abrir la web al tocar la notificación
self.addEventListener('notificationclick', event => {
  event.notification.close();
  event.waitUntil(
    clients.openWindow(event.notification.data.url || '/')
  );
});
