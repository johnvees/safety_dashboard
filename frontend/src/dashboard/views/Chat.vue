<template>
  <div class="chat-page">
    <!-- ── Sidebar: contacts ── -->
    <aside class="chat-sidebar" :class="{ 'mobile-hidden': activeUserId && isMobile }">
      <div class="chat-sidebar-head">
        <h2 class="chat-title">Chat</h2>
        <p class="chat-sub">{{ totalUnread > 0 ? `${totalUnread} pesan belum dibaca` : 'Pilih pengguna untuk memulai obrolan' }}</p>
      </div>
      <div class="chat-search">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15">
          <circle cx="11" cy="11" r="8"/>
          <line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        <input v-model="search" type="text" placeholder="Cari nama, email, BU, plant…" />
        <button v-if="search" class="search-clear" @click="search = ''">✕</button>
      </div>

      <div class="chat-userlist">
        <div v-if="loadingUsers" class="chat-loading">Memuat pengguna…</div>
        <div v-else-if="filteredGroups.length === 0" class="chat-empty">Tidak ada pengguna yang cocok.</div>

        <template v-for="grp in filteredGroups" :key="grp.name">
          <div class="chat-group-label">
            <span>{{ grp.name }}</span>
            <span class="chat-group-count">{{ grp.users.length }}</span>
          </div>
          <button
            v-for="u in grp.users"
            :key="u.id"
            class="chat-user-row"
            :class="{ active: activeUserId === u.id }"
            @click="openConversation(u)"
          >
            <div class="avatar">{{ initials(u) }}</div>
            <div class="chat-user-body">
              <div class="chat-user-row-top">
                <span class="chat-user-name">{{ displayName(u) }}</span>
                <span v-if="u.lastMessageAt" class="chat-user-time">{{ shortTime(u.lastMessageAt) }}</span>
              </div>
              <div class="chat-user-row-bot">
                <span class="chat-user-preview">
                  <span v-if="u.lastMessageFromMe" class="chat-preview-me">Anda: </span>
                  {{ u.lastMessageContent || u.email }}
                </span>
                <span v-if="u.unreadCount > 0" class="chat-unread">{{ u.unreadCount }}</span>
              </div>
              <div class="chat-user-meta">
                {{ [u.businessUnitName, u.plantName].filter(Boolean).join(' • ') || '—' }}
              </div>
            </div>
          </button>
        </template>
      </div>
    </aside>

    <!-- ── Conversation pane ── -->
    <section class="chat-pane">
      <div v-if="!activeUserId" class="chat-blank">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="56" height="56">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
        </svg>
        <h3>Tidak ada percakapan dipilih</h3>
        <p>Pilih pengguna di daftar untuk memulai mengobrol.</p>
      </div>

      <template v-else>
        <header class="chat-header">
          <button class="chat-back" @click="closeConversation" aria-label="Kembali">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="18" height="18">
              <polyline points="15 18 9 12 15 6"/>
            </svg>
          </button>
          <div class="avatar lg">{{ initials(activeUser) }}</div>
          <div class="chat-header-info">
            <div class="chat-header-name">{{ displayName(activeUser) }}</div>
            <div class="chat-header-meta">
              <span v-if="activeUser?.roleName" class="role-pill">{{ activeUser.roleName }}</span>
              {{ [activeUser?.businessUnitName, activeUser?.plantName].filter(Boolean).join(' • ') || activeUser?.email }}
            </div>
          </div>
        </header>

        <div class="chat-thread" ref="threadEl">
          <div v-if="loadingMsgs" class="chat-loading">Memuat pesan…</div>
          <div v-else-if="messages.length === 0" class="chat-empty">Belum ada pesan. Kirim sapaan pertama!</div>

          <template v-for="(m, idx) in messages" :key="m.id">
            <div v-if="showDayLabel(idx)" class="chat-day-divider">
              <span>{{ formatDay(m.createdAt) }}</span>
            </div>
            <div
              class="chat-msg"
              :class="{ me: m.senderId === currentUser.id, them: m.senderId !== currentUser.id }"
              @mouseenter="hoverId = m.id"
              @mouseleave="hoverId = null"
            >
              <div class="chat-bubble" :class="{ deleted: m.content === '__deleted__' }">
                <div v-if="editingId === m.id" class="bubble-edit">
                  <textarea v-model="editingText" rows="2" maxlength="4000" @keydown.esc="cancelEdit"></textarea>
                  <div class="bubble-edit-actions">
                    <button type="button" class="btn-cancel" @click="cancelEdit">Batal</button>
                    <button type="button" class="btn-save" :disabled="!editingText.trim() || saving" @click="saveEdit(m)">
                      {{ saving ? 'Menyimpan…' : 'Simpan' }}
                    </button>
                  </div>
                </div>
                <template v-else>
                  <div v-if="m.content === '__deleted__'" class="bubble-deleted">Pesan dihapus</div>
                  <template v-else>
                    <div v-if="m.attachmentUrl && m.attachmentType === 'image'" class="bubble-media">
                      <img :src="m.attachmentUrl" alt="gambar" @click="lightboxUrl = m.attachmentUrl" />
                      <button type="button" class="media-download" title="Unduh gambar" @click.stop="downloadMedia(m.attachmentUrl)">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                          <polyline points="7 10 12 15 17 10"/>
                          <line x1="12" y1="15" x2="12" y2="3"/>
                        </svg>
                      </button>
                    </div>
                    <div v-else-if="m.attachmentUrl && m.attachmentType === 'video'" class="bubble-media">
                      <video :src="m.attachmentUrl" controls preload="metadata"></video>
                      <button type="button" class="media-download" title="Unduh video" @click.stop="downloadMedia(m.attachmentUrl)">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                          <polyline points="7 10 12 15 17 10"/>
                          <line x1="12" y1="15" x2="12" y2="3"/>
                        </svg>
                      </button>
                    </div>
                    <div v-if="m.content" class="bubble-content">{{ m.content }}</div>
                  </template>
                  <div class="bubble-meta">
                    <span>{{ shortTime(m.createdAt) }}</span>
                    <span v-if="isEdited(m)" class="edited-tag"> · diedit</span>
                  </div>
                </template>
              </div>
              <div
                v-if="m.senderId === currentUser.id && hoverId === m.id && editingId !== m.id && m.content !== '__deleted__'"
                class="chat-msg-actions"
              >
                <button type="button" class="msg-action" title="Ubah" @click="startEdit(m)">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                  </svg>
                </button>
                <button type="button" class="msg-action danger" title="Hapus" @click="askDelete(m)">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                    <polyline points="3 6 5 6 21 6"/>
                    <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
                  </svg>
                </button>
              </div>
            </div>
          </template>
        </div>

        <div v-if="errorMsg" class="chat-error">{{ errorMsg }}</div>

        <div v-if="pendingAttachments.length" class="chat-attachment-preview">
          <div v-for="(att, i) in pendingAttachments" :key="att.id" class="attachment-thumb">
            <img v-if="att.kind === 'image'" :src="att.previewUrl" alt="preview" />
            <video v-else :src="att.previewUrl" muted></video>
            <div v-if="uploadingAttachment" class="attachment-uploading">
              <div class="spinner"></div>
            </div>
            <button type="button" class="attachment-remove" :disabled="uploadingAttachment" @click="removeAttachment(i)" aria-label="Hapus lampiran">✕</button>
          </div>
        </div>

        <form class="chat-composer" @submit.prevent="send">
          <input
            ref="fileInputEl"
            type="file"
            accept="image/*,video/*"
            multiple
            style="display:none"
            @change="onFileSelect"
          />
          <button
            type="button"
            class="btn-clip"
            :disabled="posting || uploadingAttachment"
            title="Lampirkan gambar atau video"
            @click="fileInputEl?.click()"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
              <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/>
            </svg>
          </button>
          <textarea
            v-model="draft"
            rows="1"
            maxlength="4000"
            :placeholder="pendingAttachments.length ? 'Tulis caption (opsional)…' : 'Tulis pesan…'"
            :disabled="posting"
            @keydown.enter.exact.prevent="send"
            ref="composerEl"
          ></textarea>
          <button type="submit" class="btn-send" :disabled="!canSend || posting || uploadingAttachment" title="Kirim">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
              <line x1="22" y1="2" x2="11" y2="13"/>
              <polygon points="22 2 15 22 11 13 2 9 22 2"/>
            </svg>
          </button>
        </form>
      </template>
    </section>

    <!-- Image lightbox -->
    <div v-if="lightboxUrl" class="chat-lightbox" @click.self="lightboxUrl = null" @keydown.esc="lightboxUrl = null" tabindex="0">
      <button class="lightbox-close" @click="lightboxUrl = null" aria-label="Tutup">✕</button>
      <img :src="lightboxUrl" alt="Pratinjau" />
    </div>

    <!-- Delete confirm -->
    <div v-if="deleteTarget" class="chat-confirm-overlay" @mousedown.self="deleteTarget = null">
      <div class="chat-confirm">
        <h4>Hapus Pesan?</h4>
        <p>Pesan ini akan dihapus permanen untuk Anda dan penerima.</p>
        <div class="chat-confirm-actions">
          <button type="button" class="btn-cancel" @click="deleteTarget = null">Batal</button>
          <button type="button" class="btn-danger-sm" :disabled="saving" @click="confirmDelete">
            {{ saving ? 'Menghapus…' : 'Hapus' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue';
import { authService } from '@/services/authService.js';
import { chatService, subscribeToMessages, disposeChatSocket, uploadChatMedia } from '@/services/chatService.js';

const currentUser = authService.getCurrentUser() || {};

const users = ref([]);
const loadingUsers = ref(true);
const search = ref('');

const activeUserId = ref(null);
const messages = ref([]);
const loadingMsgs = ref(false);

const draft = ref('');
const posting = ref(false);
const errorMsg = ref('');

// Selected attachments (before send): [{ id, file, kind: 'image'|'video', previewUrl }]
const pendingAttachments = ref([]);
const uploadingAttachment = ref(false);
const fileInputEl = ref(null);
const lightboxUrl = ref(null);
let attachIdSeq = 0;

const MAX_IMAGE_MB = 8;
const MAX_VIDEO_MB = 50;
const MAX_FILES = 10;

const editingId = ref(null);
const editingText = ref('');
const saving = ref(false);
const deleteTarget = ref(null);
const hoverId = ref(null);

const threadEl = ref(null);
const composerEl = ref(null);

const isMobile = ref(window.matchMedia('(max-width: 767px)').matches);
function onResize() { isMobile.value = window.matchMedia('(max-width: 767px)').matches; }
window.addEventListener('resize', onResize);

const activeUser = computed(() => users.value.find(u => u.id === activeUserId.value));
const totalUnread = computed(() => users.value.reduce((acc, u) => acc + (u.unreadCount || 0), 0));

const filteredGroups = computed(() => {
  const q = search.value.trim().toLowerCase();
  const filtered = users.value.filter(u => {
    if (!q) return true;
    const hay = [u.fullName, u.username, u.email, u.businessUnitName, u.plantName, u.roleName]
      .filter(Boolean).join(' ').toLowerCase();
    return hay.includes(q);
  });
  // Group by role name; sort groups by role level (lower level = higher rank)
  const byRole = new Map();
  for (const u of filtered) {
    const key = u.roleName || 'Tanpa Role';
    if (!byRole.has(key)) byRole.set(key, { name: key, level: u.roleLevel ?? 999, users: [] });
    byRole.get(key).users.push(u);
  }
  return Array.from(byRole.values()).sort((a, b) => a.level - b.level);
});

let unsubscribe = null;

onMounted(async () => {
  await loadUsers();
  unsubscribe = subscribeToMessages({
    onMessage: handleIncoming,
    onError: (err) => { console.warn('chat ws error', err); },
  });
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize);
  if (unsubscribe) { try { unsubscribe(); } catch { /* ignore */ } }
  disposeChatSocket();
  clearAttachment();
});

async function loadUsers() {
  loadingUsers.value = true;
  try {
    users.value = await chatService.listUsers();
  } catch (err) {
    errorMsg.value = err.message;
  } finally {
    loadingUsers.value = false;
  }
}

async function openConversation(u) {
  activeUserId.value = u.id;
  errorMsg.value = '';
  editingId.value = null;
  loadingMsgs.value = true;
  messages.value = [];
  try {
    messages.value = await chatService.listMessages(u.id);
    await chatService.markRead(u.id);
    // Clear local unread badge
    const idx = users.value.findIndex(x => x.id === u.id);
    if (idx !== -1) users.value[idx] = { ...users.value[idx], unreadCount: 0 };
  } catch (err) {
    errorMsg.value = err.message;
  } finally {
    loadingMsgs.value = false;
    await nextTick();
    scrollToBottom();
    composerEl.value?.focus();
  }
}

function closeConversation() {
  activeUserId.value = null;
  messages.value = [];
}

const canSend = computed(() => !!(draft.value.trim() || pendingAttachments.value.length));

function onFileSelect(e) {
  const files = Array.from(e.target.files || []);
  e.target.value = '';
  if (!files.length) return;
  errorMsg.value = '';
  for (const file of files) {
    if (pendingAttachments.value.length >= MAX_FILES) {
      errorMsg.value = `Maksimal ${MAX_FILES} lampiran per pengiriman`;
      break;
    }
    const ctype = (file.type || '').toLowerCase();
    let kind = null;
    if (ctype.startsWith('image/')) kind = 'image';
    else if (ctype.startsWith('video/')) kind = 'video';
    else {
      errorMsg.value = 'Hanya file gambar atau video yang diperbolehkan';
      continue;
    }
    const maxMb = kind === 'image' ? MAX_IMAGE_MB : MAX_VIDEO_MB;
    if (file.size > maxMb * 1024 * 1024) {
      errorMsg.value = `Ukuran ${file.name} terlalu besar (maks ${maxMb} MB)`;
      continue;
    }
    pendingAttachments.value.push({
      id: ++attachIdSeq,
      file,
      kind,
      previewUrl: URL.createObjectURL(file),
    });
  }
}

function removeAttachment(index) {
  const att = pendingAttachments.value[index];
  if (att?.previewUrl?.startsWith('blob:')) URL.revokeObjectURL(att.previewUrl);
  pendingAttachments.value.splice(index, 1);
}

function clearAttachment() {
  for (const att of pendingAttachments.value) {
    if (att.previewUrl?.startsWith('blob:')) URL.revokeObjectURL(att.previewUrl);
  }
  pendingAttachments.value = [];
}

async function downloadMedia(url) {
  if (!url) return;
  const name = (url.split('/').pop() || 'unduhan').split('?')[0];
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error('fetch failed');
    const blob = await res.blob();
    const blobUrl = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = blobUrl;
    a.download = name;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(blobUrl);
  } catch {
    // Fallback: open in a new tab if the blob fetch is blocked
    window.open(url, '_blank', 'noopener');
  }
}

function formatBytes(bytes) {
  if (!bytes && bytes !== 0) return '';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

async function send() {
  if (!activeUserId.value) return;
  const text = draft.value.trim();
  const attachments = pendingAttachments.value.slice();
  if (!text && !attachments.length) return;

  posting.value = true;
  errorMsg.value = '';
  try {
    if (attachments.length) {
      // Each attachment becomes its own message (WhatsApp-style); the caption
      // text is attached to the last one only.
      uploadingAttachment.value = true;
      try {
        for (let i = 0; i < attachments.length; i++) {
          const res = await uploadChatMedia(attachments[i].file);
          const isLast = i === attachments.length - 1;
          const msg = await chatService.sendMessage(activeUserId.value, {
            content: isLast ? text || null : null,
            attachmentUrl: res.url,
            attachmentType: res.type,
          });
          upsertMessage(msg);
          bumpUserPreview(activeUserId.value, msg, true);
        }
      } finally {
        uploadingAttachment.value = false;
      }
    } else {
      const msg = await chatService.sendMessage(activeUserId.value, {
        content: text || null,
      });
      upsertMessage(msg);
      bumpUserPreview(activeUserId.value, msg, true);
    }
    draft.value = '';
    clearAttachment();
    await nextTick();
    scrollToBottom();
  } catch (err) {
    errorMsg.value = err.message;
  } finally {
    posting.value = false;
  }
}

function handleIncoming(msg) {
  // Find the peer id (the user that is not me)
  const peerId = msg.senderId === currentUser.id ? msg.recipientId : msg.senderId;

  if (msg.content === '__deleted__') {
    if (activeUserId.value === peerId) {
      const idx = messages.value.findIndex(m => m.id === msg.id);
      if (idx !== -1) messages.value[idx] = { ...messages.value[idx], content: '__deleted__' };
    }
    return;
  }

  if (activeUserId.value === peerId) {
    upsertMessage(msg);
    if (msg.senderId !== currentUser.id) {
      // Mark read immediately since the conversation is open
      chatService.markRead(peerId).catch(() => {});
    }
    nextTick(scrollToBottom);
  }

  bumpUserPreview(peerId, msg, msg.senderId === currentUser.id, msg.senderId !== currentUser.id && activeUserId.value !== peerId);
}

function upsertMessage(msg) {
  const idx = messages.value.findIndex(m => m.id === msg.id);
  if (idx === -1) messages.value.push(msg);
  else messages.value[idx] = msg;
}

function previewForMessage(msg) {
  if (msg.content === '__deleted__') return '(Pesan dihapus)';
  if (msg.content) return msg.content;
  if (msg.attachmentType === 'image') return '📷 Foto';
  if (msg.attachmentType === 'video') return '🎬 Video';
  return '';
}

function bumpUserPreview(peerId, msg, fromMe, incrementUnread = false) {
  const idx = users.value.findIndex(u => u.id === peerId);
  if (idx === -1) return;
  const u = users.value[idx];
  users.value[idx] = {
    ...u,
    lastMessageContent: previewForMessage(msg),
    lastMessageAt: msg.createdAt || new Date().toISOString(),
    lastMessageFromMe: fromMe,
    unreadCount: incrementUnread ? (u.unreadCount || 0) + 1 : (u.unreadCount || 0),
  };
}

function startEdit(m) {
  editingId.value = m.id;
  editingText.value = m.content;
  errorMsg.value = '';
}
function cancelEdit() {
  editingId.value = null;
  editingText.value = '';
}
async function saveEdit(m) {
  const text = editingText.value.trim();
  if (!text) return;
  saving.value = true;
  try {
    const updated = await chatService.updateMessage(m.id, text);
    upsertMessage(updated);
    cancelEdit();
  } catch (err) {
    errorMsg.value = err.message;
  } finally {
    saving.value = false;
  }
}
function askDelete(m) {
  deleteTarget.value = m;
}
async function confirmDelete() {
  if (!deleteTarget.value) return;
  saving.value = true;
  try {
    const id = deleteTarget.value.id;
    await chatService.deleteMessage(id);
    const idx = messages.value.findIndex(m => m.id === id);
    if (idx !== -1) messages.value[idx] = { ...messages.value[idx], content: '__deleted__' };
    deleteTarget.value = null;
  } catch (err) {
    errorMsg.value = err.message;
  } finally {
    saving.value = false;
  }
}

function scrollToBottom() {
  const el = threadEl.value;
  if (!el) return;
  el.scrollTop = el.scrollHeight;
}

watch(messages, () => { nextTick(scrollToBottom); });

// ── Display helpers ────────────────────────────────────────────────────────
function displayName(u) {
  if (!u) return '';
  return u.fullName || u.username || u.email || `User #${u.id}`;
}
function initials(u) {
  const name = displayName(u);
  return name
    .split(/[\s@.]+/)
    .filter(Boolean)
    .slice(0, 2)
    .map(s => s[0].toUpperCase())
    .join('') || '?';
}
function shortTime(s) {
  if (!s) return '';
  const dt = new Date(s.replace ? s.replace(' ', 'T') : s);
  if (isNaN(dt)) return '';
  const today = new Date();
  const sameDay = dt.toDateString() === today.toDateString();
  if (sameDay) return dt.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' });
  const sameYear = dt.getFullYear() === today.getFullYear();
  return dt.toLocaleDateString('id-ID', sameYear
    ? { day: '2-digit', month: 'short' }
    : { day: '2-digit', month: 'short', year: 'numeric' });
}
function formatDay(s) {
  if (!s) return '';
  const dt = new Date(s.replace ? s.replace(' ', 'T') : s);
  if (isNaN(dt)) return '';
  const today = new Date(); today.setHours(0,0,0,0);
  const d = new Date(dt); d.setHours(0,0,0,0);
  const diff = (today - d) / (1000 * 60 * 60 * 24);
  if (diff === 0) return 'Hari ini';
  if (diff === 1) return 'Kemarin';
  return dt.toLocaleDateString('id-ID', { weekday: 'long', day: '2-digit', month: 'long', year: 'numeric' });
}
function showDayLabel(i) {
  if (i === 0) return true;
  const prev = messages.value[i - 1];
  const cur = messages.value[i];
  if (!prev?.createdAt || !cur?.createdAt) return false;
  const a = new Date(prev.createdAt.replace ? prev.createdAt.replace(' ', 'T') : prev.createdAt);
  const b = new Date(cur.createdAt.replace ? cur.createdAt.replace(' ', 'T') : cur.createdAt);
  return a.toDateString() !== b.toDateString();
}
function isEdited(m) {
  if (!m.createdAt || !m.updatedAt) return false;
  return m.createdAt !== m.updatedAt;
}
</script>

<style scoped>
.chat-page {
  height: 100%;
  min-height: 0;
  display: grid;
  grid-template-columns: 320px 1fr;
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
}

@media (max-width: 767px) {
  .chat-page { grid-template-columns: 1fr; }
  .chat-sidebar.mobile-hidden { display: none; }
}

/* Sidebar */
.chat-sidebar {
  display: flex; flex-direction: column;
  border-right: 1px solid #e2e8f0;
  background: #f8fafc;
  min-width: 0;
  min-height: 0;
  height: 100%;
}
.chat-sidebar-head { padding: 16px 16px 8px; }
.chat-title { font-size: 18px; font-weight: 700; color: #1e293b; margin: 0; }
.chat-sub { font-size: 12px; color: #64748b; margin: 4px 0 0; }

.chat-search {
  display: flex; align-items: center; gap: 8px;
  margin: 8px 16px 8px;
  background: #fff; border: 1px solid #e2e8f0; border-radius: 8px;
  padding: 0 10px;
}
.chat-search svg { color: #94a3b8; flex-shrink: 0; }
.chat-search input {
  flex: 1; border: none; outline: none; background: transparent;
  padding: 8px 0; font-size: 13px; color: #1e293b;
}
.search-clear { background: none; border: none; color: #94a3b8; cursor: pointer; font-size: 13px; }

.chat-userlist { flex: 1; overflow-y: auto; padding-bottom: 12px; }
.chat-loading, .chat-empty { padding: 16px; text-align: center; font-size: 13px; color: #94a3b8; }

.chat-group-label {
  display: flex; justify-content: space-between; align-items: center;
  font-size: 11px; font-weight: 700; color: #94a3b8;
  text-transform: uppercase; letter-spacing: 0.05em;
  padding: 10px 16px 4px;
}
.chat-group-count {
  background: #e2e8f0; color: #475569;
  border-radius: 10px; padding: 1px 7px; font-size: 11px;
}

.chat-user-row {
  width: 100%; background: none; border: none; cursor: pointer;
  display: flex; align-items: center; gap: 10px;
  padding: 10px 16px; text-align: left;
  border-left: 3px solid transparent;
  transition: background 0.12s;
}
.chat-user-row:hover { background: #eef2f7; }
.chat-user-row.active { background: #e0ecff; border-left-color: #2563eb; }

.avatar {
  flex-shrink: 0; width: 36px; height: 36px; border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8); color: #fff;
  font-size: 13px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
}
.avatar.lg { width: 42px; height: 42px; font-size: 14px; }

.chat-user-body { flex: 1; min-width: 0; }
.chat-user-row-top { display: flex; justify-content: space-between; align-items: baseline; gap: 6px; }
.chat-user-name { font-size: 13px; font-weight: 600; color: #1e293b; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.chat-user-time { font-size: 11px; color: #94a3b8; flex-shrink: 0; }
.chat-user-row-bot { display: flex; justify-content: space-between; align-items: center; gap: 6px; margin-top: 2px; }
.chat-user-preview { font-size: 12px; color: #64748b; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.chat-preview-me { color: #94a3b8; }
.chat-unread {
  background: #2563eb; color: #fff; border-radius: 10px;
  padding: 1px 7px; font-size: 11px; font-weight: 700;
  flex-shrink: 0;
}
.chat-user-meta { font-size: 11px; color: #94a3b8; margin-top: 2px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* Pane */
.chat-pane {
  display: flex; flex-direction: column;
  min-width: 0;
  min-height: 0;
  height: 100%;
  background: #fff;
}
.chat-blank {
  flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 8px; color: #94a3b8; padding: 32px;
}
.chat-blank h3 { margin: 6px 0 0; font-size: 16px; color: #475569; font-weight: 600; }
.chat-blank p { margin: 0; font-size: 13px; }
.chat-blank svg { color: #cbd5e1; }

.chat-header {
  display: flex; align-items: center; gap: 12px;
  padding: 12px 18px; border-bottom: 1px solid #e2e8f0;
  flex-shrink: 0;
}
.chat-back {
  display: none; background: none; border: none; cursor: pointer;
  color: #64748b; padding: 4px; border-radius: 6px;
}
.chat-back:hover { background: #f1f5f9; }
@media (max-width: 767px) { .chat-back { display: inline-flex; } }

.chat-header-info { flex: 1; min-width: 0; }
.chat-header-name { font-size: 15px; font-weight: 700; color: #1e293b; }
.chat-header-meta { font-size: 12px; color: #64748b; display: flex; gap: 6px; align-items: center; }
.role-pill {
  background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe;
  border-radius: 10px; padding: 1px 8px; font-size: 11px; font-weight: 600;
}

/* Thread */
.chat-thread {
  flex: 1 1 0;
  min-height: 0;
  overflow-y: auto;
  padding: 14px 18px;
  display: flex; flex-direction: column; gap: 4px;
  background: #f8fafc;
}
.chat-day-divider {
  text-align: center; margin: 10px 0 6px; position: relative;
}
.chat-day-divider span {
  background: #fff; color: #94a3b8; font-size: 11px; font-weight: 600;
  padding: 2px 10px; border-radius: 10px; border: 1px solid #e2e8f0;
}

.chat-msg {
  display: flex; align-items: flex-end; gap: 4px; margin: 2px 0;
  position: relative;
}
.chat-msg.me { justify-content: flex-end; }
.chat-msg.them { justify-content: flex-start; }
.chat-bubble {
  max-width: 70%; padding: 7px 12px;
  border-radius: 14px; font-size: 14px; line-height: 1.4;
  word-break: break-word; white-space: pre-wrap;
  box-shadow: 0 1px 1px rgba(0,0,0,0.04);
}
.chat-msg.me .chat-bubble { background: #2563eb; color: #fff; border-bottom-right-radius: 4px; }
.chat-msg.them .chat-bubble { background: #fff; color: #1e293b; border: 1px solid #e2e8f0; border-bottom-left-radius: 4px; }
.bubble-deleted { font-style: italic; opacity: 0.7; }
.chat-bubble.deleted { background: #f1f5f9 !important; color: #94a3b8 !important; border: 1px dashed #cbd5e1; }

.bubble-meta { font-size: 10px; opacity: 0.75; margin-top: 2px; }
.chat-msg.me .bubble-meta { color: #dbeafe; }
.chat-msg.them .bubble-meta { color: #94a3b8; }
.edited-tag { font-style: italic; }

.bubble-edit { display: flex; flex-direction: column; gap: 6px; min-width: 220px; }
.bubble-edit textarea {
  border: 1px solid #cbd5e1; border-radius: 8px; padding: 6px 10px;
  font-size: 13px; outline: none; resize: vertical; font-family: inherit;
  background: #fff; color: #1e293b;
}
.bubble-edit-actions { display: flex; justify-content: flex-end; gap: 6px; }
.btn-cancel {
  background: #fff; color: #64748b; border: 1px solid #e2e8f0;
  border-radius: 6px; padding: 4px 10px; font-size: 12px; cursor: pointer;
}
.btn-cancel:hover { background: #f1f5f9; color: #1e293b; }
.btn-save {
  background: #2563eb; color: #fff; border: none; border-radius: 6px;
  padding: 4px 10px; font-size: 12px; font-weight: 600; cursor: pointer;
}
.btn-save:hover:not(:disabled) { background: #1d4ed8; }
.btn-save:disabled { opacity: 0.5; cursor: not-allowed; }

.chat-msg-actions {
  display: flex; gap: 4px;
  position: absolute; top: -10px; right: 8px;
  background: #fff; border: 1px solid #e2e8f0;
  border-radius: 6px; padding: 2px; box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}
.msg-action {
  background: none; border: none; color: #64748b; cursor: pointer;
  padding: 3px 4px; border-radius: 4px;
}
.msg-action:hover { background: #f1f5f9; color: #1e293b; }
.msg-action.danger:hover { color: #dc2626; background: #fee2e2; }

.chat-error {
  background: #fee2e2; color: #991b1b; padding: 8px 14px;
  font-size: 12px;
  flex-shrink: 0;
}

.chat-attachment-preview {
  display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
  padding: 8px 14px;
  background: #f8fafc; border-top: 1px solid #e2e8f0;
  flex-shrink: 0;
}
.attachment-thumb {
  position: relative; width: 56px; height: 56px;
  border-radius: 8px; overflow: hidden;
  background: #0f172a; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
}
.attachment-thumb img, .attachment-thumb video {
  width: 100%; height: 100%; object-fit: cover;
}
.attachment-uploading {
  position: absolute; inset: 0;
  background: rgba(15, 23, 42, 0.55);
  display: flex; align-items: center; justify-content: center;
}
.spinner {
  width: 22px; height: 22px;
  border: 2px solid rgba(255,255,255,0.4);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.attachment-remove {
  position: absolute; top: 2px; right: 2px;
  background: rgba(15, 23, 42, 0.7); border: none;
  width: 18px; height: 18px; border-radius: 50%;
  color: #fff; font-size: 11px; line-height: 1; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.attachment-remove:hover:not(:disabled) { background: #dc2626; }
.attachment-remove:disabled { opacity: 0.4; cursor: not-allowed; }

.bubble-media {
  position: relative;
  display: block; max-width: 280px;
  margin: 0; border-radius: 10px; overflow: hidden;
  background: #0f172a;
}
.media-download {
  position: absolute; top: 6px; right: 6px;
  width: 30px; height: 30px; border-radius: 50%;
  background: rgba(15, 23, 42, 0.6); border: none;
  color: #fff; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  opacity: 0; transition: opacity 0.15s, background 0.15s;
}
.bubble-media:hover .media-download { opacity: 1; }
.media-download:hover { background: rgba(15, 23, 42, 0.85); }
/* Always show on touch devices where hover isn't available */
@media (hover: none) {
  .media-download { opacity: 1; }
}
.bubble-media img {
  display: block; width: 100%; max-height: 320px;
  object-fit: cover; cursor: zoom-in;
}
.bubble-media video {
  display: block; width: 100%; max-height: 360px;
  object-fit: contain; background: #000;
}
.chat-msg.me .chat-bubble:has(.bubble-media) { padding: 4px; background: #1d4ed8; }
.chat-msg.them .chat-bubble:has(.bubble-media) { padding: 4px; }
.bubble-content + .bubble-meta { margin-top: 4px; }
.bubble-media + .bubble-content { padding: 6px 8px 0; }
.chat-bubble:has(.bubble-media) .bubble-meta { padding: 0 6px 4px; }

.chat-lightbox {
  position: fixed; inset: 0;
  background: rgba(15, 23, 42, 0.92);
  z-index: 2200;
  display: flex; align-items: center; justify-content: center;
  outline: none;
}
.chat-lightbox img { max-width: 92vw; max-height: 88vh; border-radius: 8px; }
.lightbox-close {
  position: absolute; top: 16px; right: 20px;
  background: rgba(255,255,255,0.15); border: none; color: #fff;
  font-size: 20px; width: 36px; height: 36px; border-radius: 50%;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
}
.lightbox-close:hover { background: rgba(255,255,255,0.3); }

.btn-clip {
  flex-shrink: 0; display: inline-flex; align-items: center; justify-content: center;
  width: 38px; height: 38px; border-radius: 50%;
  background: transparent; color: #64748b; border: none; cursor: pointer;
  transition: background 0.15s, color 0.15s;
}
.btn-clip:hover:not(:disabled) { background: #f1f5f9; color: #1e293b; }
.btn-clip:disabled { opacity: 0.4; cursor: not-allowed; }

.chat-composer {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 14px;
  border-top: 1px solid #e2e8f0;
  background: #fff;
  flex-shrink: 0;
}
.chat-composer textarea {
  flex: 1; border: 1px solid #e2e8f0; border-radius: 18px;
  padding: 9px 14px; font-size: 14px; color: #1e293b;
  outline: none; resize: none; min-height: 38px; max-height: 140px;
  font-family: inherit; background: #f8fafc;
  transition: border-color 0.15s, background 0.15s;
}
.chat-composer textarea:focus { border-color: #3b82f6; background: #fff; }
.btn-send {
  flex-shrink: 0; display: inline-flex; align-items: center; justify-content: center;
  width: 38px; height: 38px; border-radius: 50%;
  background: #2563eb; color: #fff; border: none; cursor: pointer;
  transition: background 0.15s;
}
.btn-send:hover:not(:disabled) { background: #1d4ed8; }
.btn-send:disabled { opacity: 0.5; cursor: not-allowed; }

/* Confirm overlay */
.chat-confirm-overlay {
  position: fixed; inset: 0; background: rgba(15, 23, 42, 0.5);
  z-index: 2100; display: flex; align-items: center; justify-content: center;
}
.chat-confirm {
  background: #fff; border-radius: 12px; padding: 20px 22px;
  max-width: 360px; width: 90%;
  box-shadow: 0 12px 40px rgba(0,0,0,0.18);
}
.chat-confirm h4 { margin: 0 0 6px; font-size: 16px; color: #1e293b; }
.chat-confirm p { margin: 0 0 16px; font-size: 13px; color: #475569; }
.chat-confirm-actions { display: flex; gap: 8px; justify-content: flex-end; }
.btn-danger-sm {
  background: #dc2626; color: #fff; border: none; border-radius: 7px;
  padding: 6px 14px; font-size: 13px; font-weight: 600; cursor: pointer;
}
.btn-danger-sm:hover:not(:disabled) { background: #b91c1c; }
.btn-danger-sm:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
