<template>
  <header class="topbar">
    <div class="topbar-left">
      <button class="btn-hamburger" @click="emit('toggle-sidebar')" aria-label="Toggle sidebar">
        <span></span><span></span><span></span>
      </button>
      <div class="page-title">{{ title }}</div>
    </div>
    <div class="topbar-right">
      <!-- Bell notification -->
      <div class="notif-wrap" ref="notifWrap">
        <button class="btn-icon" @click="toggleDropdown" aria-label="Notifikasi">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
            <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
          </svg>
          <span v-if="unreadCount > 0" class="badge">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
        </button>

        <!-- Dropdown -->
        <div v-if="open" class="notif-dropdown">
          <div class="notif-header">
            <span class="notif-header-title">Notifikasi</span>
            <button v-if="notifications.length > 0" class="notif-mark-all" @click="markAllRead">
              Tandai sudah dibaca
            </button>
          </div>

          <div v-if="loading" class="notif-empty">Memuat...</div>
          <div v-else-if="notifications.length === 0" class="notif-empty">
            Tidak ada notifikasi
          </div>
          <div v-else class="notif-list">
            <div
              v-for="n in notifications"
              :key="n.id"
              class="notif-item"
              :class="{ unread: !n.isRead }"
              @click="handleNotifClick(n)"
            >
              <div class="notif-icon" :class="iconClass(n.type)">
                <svg v-if="n.type === 'new_chat'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                </svg>
                <svg v-else-if="n.type.startsWith('delete_')" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4h6v2"/>
                </svg>
                <svg v-else-if="n.type.startsWith('update_')" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/>
                </svg>
              </div>
              <div class="notif-body">
                <div class="notif-title">{{ n.title }}</div>
                <div v-if="n.message" class="notif-message">{{ n.message }}</div>
                <div class="notif-time">{{ timeAgo(n.createdAt) }}</div>
              </div>
              <div v-if="!n.isRead" class="notif-dot"></div>
            </div>
          </div>
        </div>
      </div>

    </div>
  </header>

  <!-- Chat toast stack (teleported to body so it's above everything) -->
  <Teleport to="body">
    <div class="toast-stack">
      <transition-group name="toast">
        <div
          v-for="t in toasts"
          :key="t._key"
          class="toast-item"
          @click="handleToastClick(t)"
        >
          <div class="toast-icon" :class="iconClass(t.notif.type)">
            <svg v-if="t.notif.type === 'new_chat'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
            <svg v-else-if="t.notif.type.startsWith('delete_')" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4h6v2"/>
            </svg>
            <svg v-else-if="t.notif.type.startsWith('update_')" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/>
            </svg>
          </div>
          <div class="toast-body">
            <div class="toast-title">{{ t.notif.title }}</div>
            <div v-if="t.notif.message" class="toast-message">{{ t.notif.message }}</div>
          </div>
          <div class="toast-progress">
            <div class="toast-progress-bar" :style="{ animationDuration: TOAST_DURATION + 'ms' }"></div>
          </div>
          <button class="toast-close" @click.stop="dismissToast(t)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
      </transition-group>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { createClient } from "graphql-ws";
import { enablePush, registerServiceWorker } from "@/services/pushService.js";
import { updateBadge } from "@/services/badge.js";

const props = defineProps({
  title: { type: String, default: "Dashboard" },
});

const emit = defineEmits(["toggle-sidebar"]);

const router = useRouter();

// ── Notifications ──────────────────────────────────────────────────
const open = ref(false);
const loading = ref(false);
const notifications = ref([]);
const notifWrap = ref(null);
const pendingDeletes = new Set(); // IDs deleted locally but not yet confirmed by DB

const unreadCount = computed(() => notifications.value.filter((n) => !n.isRead).length);
// Tab title + favicon badge reflect unread bell items plus any live toasts.
const totalBadge = computed(() => unreadCount.value + toasts.value.length);

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
const GRAPHQL_URL = `${API_BASE}/graphql`;
const WS_URL = GRAPHQL_URL.replace(/^http/, "ws");

async function gql(query, variables = {}) {
  const token = localStorage.getItem("token");
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(GRAPHQL_URL, { method: "POST", headers, body: JSON.stringify({ query, variables }) });
  const { data, errors } = await res.json();
  if (errors?.length) throw new Error(errors[0].message);
  return data;
}

async function fetchNotifications() {
  try {
    loading.value = true;
    const data = await gql(`query { myNotifications { id type title message link isRead createdAt } }`);
    // Filter out anything we already deleted locally (race condition guard)
    notifications.value = data.myNotifications.filter((n) => !pendingDeletes.has(n.id));
  } catch (_) {
    // silent
  } finally {
    loading.value = false;
  }
}

async function deleteNotification(id) {
  pendingDeletes.add(id);
  try {
    await gql(`mutation M($id: Int!) { deleteNotification(id: $id) { success } }`, { id });
  } catch (_) {
    // On failure restore so UI can retry
    pendingDeletes.delete(id);
  } finally {
    // Clean up after confirmed delete (success path)
    // Keep in set until next fetch cycle naturally removes it
    setTimeout(() => pendingDeletes.delete(id), 5000);
  }
}

async function markAllRead() {
  try {
    await gql(`mutation { markAllNotificationsRead { success } }`);
    notifications.value = [];
    pendingDeletes.clear();
  } catch (_) {}
}

async function handleNotifClick(n) {
  notifications.value = notifications.value.filter((x) => x.id !== n.id);
  open.value = false;
  if (n.id > 0) await deleteNotification(n.id);
  if (n.link) {
    const isSamePath = router.currentRoute.value.path === n.link;
    if (isSamePath) {
      // Force remount by appending a refresh token — router-view keyed on fullPath will re-mount
      router.push({ path: n.link, query: { _r: Date.now() } });
    } else {
      router.push(n.link);
    }
  }
}

function toggleDropdown() {
  open.value = !open.value;
  if (open.value && notifications.value.length === 0) fetchNotifications();
}

// Close on outside click
function onOutsideClick(e) {
  if (notifWrap.value && !notifWrap.value.contains(e.target)) {
    open.value = false;
  }
}

// ── Toast (chat notifications only, tab visible) ──────────────────
const TOAST_DURATION = 8000; // ms
const toasts = ref([]);
let toastKey = 0;

function showToast(notif) {
  const key = ++toastKey;
  const entry = { _key: key, notif, timer: null };
  entry.timer = setTimeout(() => moveToastToBell(key), TOAST_DURATION);
  toasts.value.unshift(entry);
}

function moveToastToBell(key) {
  const idx = toasts.value.findIndex((t) => t._key === key);
  if (idx === -1) return;
  const [entry] = toasts.value.splice(idx, 1);
  clearTimeout(entry.timer);
  // Add to bell list if not a duplicate
  const exists = entry.notif.id > 0 && notifications.value.some((x) => x.id === entry.notif.id);
  if (!exists) notifications.value.unshift(entry.notif);
}

function dismissToast(t) {
  // X button — move to bell list
  moveToastToBell(t._key);
}

async function handleToastClick(t) {
  clearTimeout(t.timer);
  toasts.value = toasts.value.filter((x) => x._key !== t._key);
  if (t.notif.id > 0) await deleteNotification(t.notif.id);
  if (t.notif.link) {
    const isSamePath = router.currentRoute.value.path === t.notif.link;
    if (isSamePath) {
      router.push({ path: t.notif.link, query: { _r: Date.now() } });
    } else {
      router.push(t.notif.link);
    }
  }
}

// ── WebSocket subscription ─────────────────────────────────────────
let wsClient = null;
let wsUnsub = null;

function startSubscription() {
  wsClient = createClient({
    url: WS_URL,
    lazy: true,
    retryAttempts: 10,
    keepAlive: 20_000,
    connectionParams: () => {
      const token = localStorage.getItem("token");
      return token ? { authorization: `Bearer ${token}` } : {};
    },
  });

  wsUnsub = wsClient.subscribe(
    { query: `subscription { notificationStream { id type title message link isRead createdAt } }` },
    {
      next({ data }) {
        const n = data?.notificationStream;
        if (!n) return;

        // Show toast if tab is active, otherwise go straight to bell
        if (document.visibilityState === "visible") {
          showToast(n);
          return;
        }

        // Tab hidden: add directly to bell list
        const exists = n.id > 0 && notifications.value.some((x) => x.id === n.id);
        if (!exists) notifications.value.unshift(n);
      },
      error() { /* reconnect handled by graphql-ws */ },
      complete() {},
    },
  );
}

function stopSubscription() {
  if (wsUnsub) { try { wsUnsub(); } catch { /**/ } wsUnsub = null; }
  if (wsClient) { try { wsClient.dispose(); } catch { /**/ } wsClient = null; }
}

// Keep the tab title + favicon badge in sync with the unread count.
watch(totalBadge, (n) => updateBadge(n), { immediate: true });

onMounted(() => {
  fetchNotifications();
  startSubscription();
  document.addEventListener("click", onOutsideClick);
  // Register the service worker and (best-effort) subscribe for OS/phone push.
  registerServiceWorker().catch(() => {});
  enablePush().catch(() => {});
});
onUnmounted(() => {
  stopSubscription();
  document.removeEventListener("click", onOutsideClick);
  // Clear all toast timers
  toasts.value.forEach((t) => clearTimeout(t.timer));
});

// ── Helpers ────────────────────────────────────────────────────────
function iconClass(type) {
  if (type.startsWith("delete_")) return "icon-delete";
  if (type.startsWith("update_")) return "icon-update";
  if (type === "new_chat") return "icon-chat";
  return "icon-new";
}

function timeAgo(ts) {
  if (!ts) return "";
  const d = new Date(ts.replace(" ", "T"));
  const diff = (Date.now() - d.getTime()) / 1000;
  if (diff < 60) return "Baru saja";
  if (diff < 3600) return `${Math.floor(diff / 60)} mnt lalu`;
  if (diff < 86400) return `${Math.floor(diff / 3600)} jam lalu`;
  return `${Math.floor(diff / 86400)} hari lalu`;
}

</script>

<style scoped>
.topbar {
  height: 60px;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  flex-shrink: 0;
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-hamburger {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 5px;
  width: 32px;
  height: 32px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  transition: background 0.15s;
}

.btn-hamburger:hover { background: #f1f5f9; }

.btn-hamburger span {
  display: block;
  height: 2px;
  width: 100%;
  background: #475569;
  border-radius: 2px;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* ── Bell button ── */
.notif-wrap {
  position: relative;
}

.btn-icon {
  position: relative;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: none;
  border: 1px solid #e5e7eb;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #475569;
  transition: background 0.15s, color 0.15s;
}

.btn-icon:hover {
  background: #f1f5f9;
  color: #1e293b;
}

.btn-icon svg {
  width: 17px;
  height: 17px;
}

.badge {
  position: absolute;
  top: -5px;
  right: -5px;
  min-width: 17px;
  height: 17px;
  padding: 0 4px;
  background: #ef4444;
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  box-sizing: border-box;
}

/* ── Dropdown ── */
.notif-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 380px;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.13);
  display: flex;
  flex-direction: column;
  z-index: 999;
  overflow: hidden;
}

@media (max-width: 768px) {
  .notif-dropdown { width: 320px; }
}

@media (max-width: 480px) {
  .notif-dropdown {
    position: fixed;
    top: 68px;
    left: 12px;
    right: 12px;
    width: auto;
  }
}

.notif-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px 12px;
  border-bottom: 1px solid #f1f5f9;
  flex-shrink: 0;
}

.notif-header-title {
  font-size: 14px;
  font-weight: 700;
  color: #1e293b;
}

.notif-mark-all {
  background: none;
  border: none;
  font-size: 12px;
  color: #ef4444;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  font-weight: 500;
  transition: background 0.15s;
}

.notif-mark-all:hover { background: #fee2e2; }

.notif-empty {
  padding: 40px 16px;
  text-align: center;
  font-size: 13px;
  color: #94a3b8;
}

.notif-list {
  overflow-y: auto;
  max-height: 360px;
  overscroll-behavior: contain;
  -webkit-overflow-scrolling: touch;
}

.notif-list::-webkit-scrollbar { width: 4px; }
.notif-list::-webkit-scrollbar-track { background: transparent; }
.notif-list::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 4px; }

@media (max-width: 480px) {
  .notif-list { max-height: calc(100vh - 160px); }
}

.notif-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px 16px;
  cursor: pointer;
  border-bottom: 1px solid #f8fafc;
  transition: background 0.12s;
  position: relative;
}

.notif-item:last-child { border-bottom: none; }
.notif-item:hover { background: #f8fafc; }
.notif-item.unread { background: #eff6ff; }
.notif-item.unread:hover { background: #dbeafe; }

.notif-icon {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.notif-icon svg { width: 16px; height: 16px; }

.icon-new    { background: #dcfce7; color: #16a34a; }
.icon-chat   { background: #ede9fe; color: #7c3aed; }
.icon-update { background: #dbeafe; color: #2563eb; }
.icon-delete { background: #fee2e2; color: #dc2626; }

.notif-body {
  flex: 1;
  min-width: 0;
}

.notif-title {
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.notif-message {
  font-size: 12px;
  color: #64748b;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.notif-time {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 4px;
}

.notif-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #3b82f6;
  flex-shrink: 0;
  margin-top: 4px;
}

</style>

<!-- Toast styles are NOT scoped (teleported outside component root) -->
<style>
.toast-stack {
  position: fixed;
  top: 72px;
  right: 24px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 9999;
  pointer-events: none;
  max-height: calc(100vh - 80px);
  overflow: hidden;
}

.toast-item {
  pointer-events: all;
  display: flex;
  align-items: flex-start;
  gap: 10px;
  width: 340px;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  box-shadow: 0 8px 28px rgba(0,0,0,0.14);
  padding: 14px 14px 18px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: transform 0.15s, box-shadow 0.15s;
}

.toast-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(0,0,0,0.18);
}

.toast-item .toast-icon {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.toast-item .icon-new    { background: #dcfce7; color: #16a34a; }
.toast-item .icon-chat   { background: #ede9fe; color: #7c3aed; }
.toast-item .icon-update { background: #dbeafe; color: #2563eb; }
.toast-item .icon-delete { background: #fee2e2; color: #dc2626; }

.toast-item .toast-icon svg {
  width: 16px;
  height: 16px;
}

.toast-body {
  flex: 1;
  min-width: 0;
}

.toast-title {
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.toast-message {
  font-size: 12px;
  color: #64748b;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.toast-close {
  background: none;
  border: none;
  cursor: pointer;
  padding: 2px;
  color: #94a3b8;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background 0.12s, color 0.12s;
}

.toast-close:hover {
  background: #f1f5f9;
  color: #475569;
}

.toast-close svg {
  width: 14px;
  height: 14px;
}

/* Progress bar at bottom of toast */
.toast-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: #f1f5f9;
}

.toast-progress-bar {
  height: 100%;
  background: #7c3aed;
  width: 100%;
  animation: toast-shrink linear forwards;
}

@keyframes toast-shrink {
  from { width: 100%; }
  to   { width: 0%; }
}

/* Enter/leave transitions */
.toast-enter-active { transition: opacity 0.25s ease, transform 0.25s ease; }
.toast-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.toast-enter-from   { opacity: 0; transform: translateX(40px); }
.toast-leave-to     { opacity: 0; transform: translateX(40px); }

@media (max-width: 480px) {
  .toast-stack {
    top: 68px;
    left: 12px;
    right: 12px;
  }
  .toast-item {
    width: auto;
  }
}
</style>
