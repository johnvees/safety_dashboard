/* Service worker for Web Push notifications (Safety Dashboard).
 * Receives pushes from the backend and shows native OS/phone notifications
 * even when the site/browser is fully closed. */

self.addEventListener("install", () => {
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(self.clients.claim());
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
