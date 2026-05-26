const CACHE_NAME = 'beer-top100-v20260526-1';
const APP_SHELL = [
  './',
  './index.html',
  './history.html',
  './manifest.webmanifest',
  './icon.svg',
  './tradingview-notes.user.js'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(APP_SHELL))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.map(key => {
          if (key !== CACHE_NAME) {
            console.log('[SW] Deleting old cache:', key);
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

function normalizedLocalRequest(request) {
  const url = new URL(request.url);
  url.searchParams.delete('_');
  return new Request(url.toString(), { method: 'GET' });
}

async function networkFirst(request) {
  const cacheKey = normalizedLocalRequest(request);
  try {
    const response = await fetch(request);
    const copy = response.clone();
    const cache = await caches.open(CACHE_NAME);
    await cache.put(cacheKey, copy);
    return response;
  } catch(e) {
    const cached = await caches.match(cacheKey);
    if (cached) return cached;
    throw e;
  }
}

async function cacheFirst(request) {
  const cacheKey = normalizedLocalRequest(request);
  const cached = await caches.match(cacheKey);
  if (cached) return cached;

  const response = await fetch(request);
  const cache = await caches.open(CACHE_NAME);
  await cache.put(cacheKey, response.clone());
  return response;
}

self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin) return;

  // Always prefer network to get the freshest data (index.html, data, notes, etc.)
  // Fallback to cache if network is down.
  event.respondWith(networkFirst(event.request));
});
