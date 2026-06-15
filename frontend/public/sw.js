/* Service worker for the Safety Dashboard PWA.
 * 1. Web Push: receives pushes from the backend and shows native OS/phone
 *    notifications even when the site/browser is fully closed.
 * 2. Offline app shell: caches the built assets so the installed PWA opens
 *    instantly and works without a connection. */

const CACHE = "safety-dashboard-v1";
const APP_SHELL = ["/", "/index.html", "/CPIN.JK.png", "/manifest.webmanifest"];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches
      .open(CACHE)
      .then((cache) => cache.addAll(APP_SHELL))
      .catch(() => {}),
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    Promise.all([
      // Drop old caches from previous deploys.
      caches
        .keys()
        .then((keys) =>
          Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))),
        ),
      self.clients.claim(),
    ]),
  );
});

self.addEventListener("fetch", (event) => {
  const req = event.request;

  // Only handle same-origin GET; let API calls and cross-origin requests
  // (e.g. the backend) go straight to the network.
  if (req.method !== "GET" || new URL(req.url).origin !== self.location.origin) {
    return;
  }

  // SPA navigations: network-first, fall back to the cached app shell offline.
  if (req.mode === "navigate") {
    event.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE).then((cache) => cache.put("/index.html", copy));
          return res;
        })
        .catch(() => caches.match("/index.html").then((r) => r || caches.match("/"))),
    );
    return;
  }

  // Static assets: cache-first, then network (and cache the result).
  event.respondWith(
    caches.match(req).then(
      (cached) =>
        cached ||
        fetch(req).then((res) => {
          if (res && res.status === 200 && res.type === "basic") {
            const copy = res.clone();
            caches.open(CACHE).then((cache) => cache.put(req, copy));
          }
          return res;
        }),
    ),
  );
});

self.addEventListener("push", (event) => {
  let data = {};
  try {
    data = event.data ? event.data.json() : {};
  } catch (e) {
    data = { title: "Safety Dashboard", body: event.data ? event.data.text() : "" };
  }

  const title = data.title || "Safety Dashboard";
  const options = {
    body: data.body || "",
    icon: "/CPIN.JK.png",
    badge: "/CPIN.JK.png",
    tag: data.tag || undefined,
    renotify: Boolean(data.tag),
    data: { url: data.url || "/" },
  };

  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const url = (event.notification.data && event.notification.data.url) || "/";

  event.waitUntil(
    self.clients
      .matchAll({ type: "window", includeUncontrolled: true })
      .then((clientList) => {
        for (const client of clientList) {
          if ("focus" in client) {
            client.focus();
            if ("navigate" in client && url) {
              try {
                client.navigate(url);
              } catch (e) {
                /* cross-origin or unsupported — ignore */
              }
            }
            return undefined;
          }
        }
        if (self.clients.openWindow) return self.clients.openWindow(url);
        return undefined;
      }),
  );
});
