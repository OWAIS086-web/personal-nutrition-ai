// Personal Nutrition AI Service Worker
const CACHE_NAME = "nutrition-ai-v1"
const urlsToCache = [
  "/",
  "/static/css/main.css",
  "/static/js/main.js",
  "/static/js/meal-editor.js",
  "/static/js/ai-coach.js",
  "/static/manifest.json",
]

// Install event - cache resources
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches
      .open(CACHE_NAME)
      .then((cache) => {
        console.log("[SW] Caching app shell")
        return cache.addAll(urlsToCache)
      })
      .catch((err) => {
        console.log("[SW] Cache failed:", err)
      }),
  )
})

// Fetch event - serve from cache, fallback to network
self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches
      .match(event.request)
      .then((response) => {
        // Return cached version or fetch from network
        return response || fetch(event.request)
      })
      .catch(() => {
        // Fallback for navigation requests
        if (event.request.mode === "navigate") {
          return caches.match("/")
        }
      }),
  )
})

// Activate event - clean up old caches
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log("[SW] Deleting old cache:", cacheName)
            return caches.delete(cacheName)
          }
        }),
      )
    }),
  )
})
