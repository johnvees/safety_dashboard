// Web Push subscription management (service worker + VAPID).
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
const GRAPHQL_URL = `${API_BASE}/graphql`;

async function gql(query, variables = {}) {
  const token = localStorage.getItem("token");
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(GRAPHQL_URL, {
    method: "POST",
    headers,
    body: JSON.stringify({ query, variables }),
  });
  const { data, errors } = await res.json();
  if (errors?.length) throw new Error(errors[0].message);
  return data;
}

function urlBase64ToUint8Array(base64String) {
  const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
  const raw = atob(base64);
  const out = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; i += 1) out[i] = raw.charCodeAt(i);
  return out;
}

let swRegistration = null;

export function pushSupported() {
  return (
    "serviceWorker" in navigator &&
    "PushManager" in window &&
    "Notification" in window
  );
}

export async function registerServiceWorker() {
  if (!pushSupported()) return null;
  if (!swRegistration) {
    swRegistration = await navigator.serviceWorker.register("/sw.js");
  }
  return swRegistration;
}

// Request permission, subscribe with the server VAPID key, persist to backend.
// Returns { ok: boolean, reason: string }.
export async function enablePush() {
  if (!pushSupported()) return { ok: false, reason: "unsupported" };

  const reg = await registerServiceWorker();
  if (!reg) return { ok: false, reason: "unsupported" };

  let permission = Notification.permission;
  if (permission === "default") permission = await Notification.requestPermission();
  if (permission !== "granted") return { ok: false, reason: permission };

  let pushPublicKey = "";
  try {
    ({ pushPublicKey } = await gql(`query { pushPublicKey }`));
  } catch (e) {
    return { ok: false, reason: "no-server-key" };
  }
  if (!pushPublicKey) return { ok: false, reason: "no-server-key" };

  await navigator.serviceWorker.ready;
  let sub = await reg.pushManager.getSubscription();
  if (!sub) {
    sub = await reg.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(pushPublicKey),
    });
  }

  const json = sub.toJSON();
  await gql(
    `mutation Save($endpoint: String!, $p256dh: String!, $auth: String!, $userAgent: String) {
      savePushSubscription(endpoint: $endpoint, p256dh: $p256dh, auth: $auth, userAgent: $userAgent) {
        success message
      }
    }`,
    {
      endpoint: json.endpoint,
      p256dh: json.keys.p256dh,
      auth: json.keys.auth,
      userAgent: navigator.userAgent,
    },
  );
  return { ok: true, reason: "granted" };
}

// Unsubscribe this browser and remove the row from the backend (on logout).
export async function disablePush() {
  if (!pushSupported()) return;
  try {
    const reg = await navigator.serviceWorker.getRegistration();
    if (!reg) return;
    const sub = await reg.pushManager.getSubscription();
    if (!sub) return;
    const { endpoint } = sub;
    await sub.unsubscribe().catch(() => {});
    await gql(
      `mutation Del($endpoint: String!) { deletePushSubscription(endpoint: $endpoint) { success } }`,
      { endpoint },
    ).catch(() => {});
  } catch (e) {
    /* ignore */
  }
}
