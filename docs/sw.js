const CACHE_NAME = 'beer-top100-v20260525-1';
const APP_SHELL = [
  './',
  './index.html',
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
    caches.keys()
      .then(keys => Promise.all(keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))))
      .then(() => self.clients.claim())
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

  if (url.pathname.includes('/data/') || url.pathname.includes('/notes/')) {
    event.respondWith(networkFirst(event.request));
    return;
  }

  event.respondWith(cacheFirst(event.request));
});
