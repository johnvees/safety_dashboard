<template>
  <div class="comment-section">
    <div class="comment-header">
      <h4 class="comment-title">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
        </svg>
        Komentar <span class="comment-count">({{ comments.length }})</span>
      </h4>
    </div>

    <div v-if="loading" class="comment-loading">
      <div class="spinner"></div>
      <span>Memuat komentar…</span>
    </div>

    <div v-else-if="comments.length === 0" class="comment-empty">
      Belum ada komentar. Jadilah yang pertama berkomentar.
    </div>

    <ul v-else class="comment-list">
      <li v-for="c in comments" :key="c.id" class="comment-item">
        <div class="avatar">{{ initials(c) }}</div>
        <div class="comment-body">
          <div class="comment-meta">
            <span class="comment-author">{{ displayName(c) }}</span>
            <span class="comment-time">{{ formatTime(c.createdAt) }}<span v-if="isEdited(c)" class="edited-tag"> · diedit</span></span>
          </div>

          <div v-if="editingId === c.id" class="comment-edit">
            <textarea v-model="editingText" rows="2" maxlength="2000" class="comment-textarea" @keydown.esc="cancelEdit"></textarea>
            <div class="comment-edit-actions">
              <button type="button" class="btn-cancel" @click="cancelEdit">Batal</button>
              <button type="button" class="btn-save" :disabled="!editingText.trim() || saving" @click="saveEdit(c)">
                {{ saving ? 'Menyimpan…' : 'Simpan' }}
              </button>
            </div>
          </div>

          <div v-else class="comment-content">{{ c.content }}</div>

          <div v-if="editingId !== c.id && (c.canEdit || c.canDelete)" class="comment-actions">
            <button v-if="c.canEdit" type="button" class="comment-action" @click="startEdit(c)">Ubah</button>
            <button v-if="c.canDelete" type="button" class="comment-action danger" @click="askDelete(c)">Hapus</button>
          </div>
        </div>
      </li>
    </ul>

    <div class="comment-compose">
      <textarea
        v-model="newContent"
        rows="2"
        maxlength="2000"
        placeholder="Tulis komentar…"
        class="comment-textarea"
        :disabled="posting"
        @keydown.enter.exact.prevent="postComment"
      ></textarea>
      <div class="comment-compose-row">
        <span class="comment-counter">{{ newContent.length }}/2000</span>
        <button type="button" class="btn-post" :disabled="!newContent.trim() || posting" @click="postComment">
          {{ posting ? 'Mengirim…' : 'Kirim' }}
        </button>
      </div>
    </div>

    <div v-if="errorMsg" class="comment-error">{{ errorMsg }}</div>

    <!-- Delete confirm -->
    <div v-if="deleteTarget" class="cs-confirm-overlay" @mousedown.self="deleteTarget = null">
      <div class="cs-confirm">
        <h4>Hapus Komentar?</h4>
        <p>Komentar ini akan dihapus permanen.</p>
        <div class="cs-confirm-actions">
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
import { ref, watch, onMounted } from 'vue';
import { commentsService } from '@/services/commentsService.js';

const props = defineProps({
  reportType: { type: String, required: true }, // 'inspection_k3l' | 'hse_daily'
  reportId: { type: Number, required: true },
});

const emit = defineEmits(['count-change']);

const comments = ref([]);
const loading = ref(true);
const posting = ref(false);
const saving = ref(false);
const newContent = ref('');
const editingId = ref(null);
const editingText = ref('');
const errorMsg = ref('');
const deleteTarget = ref(null);

async function load() {
  loading.value = true;
  errorMsg.value = '';
  try {
    comments.value = await commentsService.list(props.reportType, props.reportId);
    emit('count-change', comments.value.length);
  } catch (err) {
    errorMsg.value = err.message;
  } finally {
    loading.value = false;
  }
}

onMounted(load);
watch(() => [props.reportType, props.reportId], load);

async function postComment() {
  const text = newContent.value.trim();
  if (!text) return;
  posting.value = true;
  errorMsg.value = '';
  try {
    const c = await commentsService.create(props.reportType, props.reportId, text);
    comments.value.push(c);
    newContent.value = '';
    emit('count-change', comments.value.length);
  } catch (err) {
    errorMsg.value = err.message;
  } finally {
    posting.value = false;
  }
}

function startEdit(c) {
  editingId.value = c.id;
  editingText.value = c.content;
  errorMsg.value = '';
}

function cancelEdit() {
  editingId.value = null;
  editingText.value = '';
}

async function saveEdit(c) {
  const text = editingText.value.trim();
  if (!text) return;
  saving.value = true;
  errorMsg.value = '';
  try {
    const updated = await commentsService.update(c.id, text);
    const idx = comments.value.findIndex(x => x.id === c.id);
    if (idx !== -1) comments.value[idx] = updated;
    cancelEdit();
  } catch (err) {
    errorMsg.value = err.message;
  } finally {
    saving.value = false;
  }
}

function askDelete(c) {
  deleteTarget.value = c;
  errorMsg.value = '';
}

async function confirmDelete() {
  if (!deleteTarget.value) return;
  saving.value = true;
  try {
    await commentsService.delete(deleteTarget.value.id);
    comments.value = comments.value.filter(x => x.id !== deleteTarget.value.id);
    deleteTarget.value = null;
    emit('count-change', comments.value.length);
  } catch (err) {
    errorMsg.value = err.message;
  } finally {
    saving.value = false;
  }
}

function displayName(c) {
  return c.userFullName || c.userUsername || c.userEmail || `User #${c.userId}`;
}

function initials(c) {
  const name = displayName(c);
  return name
    .split(/[\s@.]+/)
    .filter(Boolean)
    .slice(0, 2)
    .map(s => s[0].toUpperCase())
    .join('') || '?';
}

function formatTime(s) {
  if (!s) return '';
  const dt = new Date(s.replace ? s.replace(' ', 'T') : s);
  if (isNaN(dt)) return '';
  const date = dt.toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' });
  const time = dt.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' });
  return `${date} ${time}`;
}

function isEdited(c) {
  if (!c.createdAt || !c.updatedAt) return false;
  return c.createdAt !== c.updatedAt;
}
</script>

<style scoped>
.comment-section { display: flex; flex-direction: column; gap: 10px; }
.comment-header { display: flex; align-items: center; justify-content: space-between; }
.comment-title {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 12px; font-weight: 700; color: #64748b;
  text-transform: uppercase; letter-spacing: 0.05em;
  margin: 0; padding-bottom: 4px;
  border-bottom: 1px solid #e2e8f0;
  width: 100%;
}
.comment-count { color: #94a3b8; font-weight: 600; }
.comment-loading {
  display: flex; align-items: center; gap: 8px;
  font-size: 13px; color: #94a3b8; padding: 8px 4px;
}
.comment-empty {
  font-size: 13px; color: #94a3b8; padding: 8px 4px;
}
.comment-loading .spinner {
  width: 16px; height: 16px;
  border: 2px solid #e2e8f0; border-top-color: #3b82f6;
  border-radius: 50%; animation: spin 0.7s linear infinite; flex-shrink: 0;
}
@keyframes spin { to { transform: rotate(360deg); } }

.comment-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 10px; }
.comment-item { display: flex; gap: 10px; padding: 10px 12px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; }
.avatar {
  flex-shrink: 0; width: 32px; height: 32px; border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8); color: #fff;
  font-size: 12px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
}
.comment-body { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 4px; }
.comment-meta { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.comment-author { font-size: 13px; font-weight: 600; color: #1e293b; }
.comment-time { font-size: 11px; color: #94a3b8; }
.edited-tag { font-style: italic; }
.comment-content { font-size: 13px; color: #334155; white-space: pre-wrap; word-break: break-word; }
.comment-actions { display: flex; gap: 10px; margin-top: 2px; }
.comment-action { background: none; border: none; padding: 0; font-size: 12px; color: #64748b; cursor: pointer; }
.comment-action:hover { color: #1e293b; text-decoration: underline; }
.comment-action.danger { color: #dc2626; }
.comment-action.danger:hover { color: #b91c1c; }

.comment-edit { display: flex; flex-direction: column; gap: 6px; }
.comment-edit-actions { display: flex; gap: 8px; justify-content: flex-end; }

.comment-compose { display: flex; flex-direction: column; gap: 6px; padding-top: 6px; }
.comment-textarea {
  width: 100%; box-sizing: border-box; border: 1px solid #e2e8f0; border-radius: 8px;
  padding: 8px 12px; font-size: 13px; color: #1e293b; background: #fff;
  outline: none; resize: vertical; font-family: inherit;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.comment-textarea:focus { border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.12); }
.comment-compose-row { display: flex; align-items: center; justify-content: space-between; }
.comment-counter { font-size: 11px; color: #94a3b8; }

.btn-post {
  background: #3b82f6; color: #fff; border: none; border-radius: 7px;
  padding: 6px 14px; font-size: 13px; font-weight: 600; cursor: pointer;
  transition: background 0.15s;
}
.btn-post:hover:not(:disabled) { background: #2563eb; }
.btn-post:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-cancel {
  background: #fff; color: #64748b; border: 1px solid #e2e8f0; border-radius: 7px;
  padding: 5px 12px; font-size: 12px; cursor: pointer;
}
.btn-cancel:hover { background: #f1f5f9; color: #1e293b; }
.btn-save {
  background: #3b82f6; color: #fff; border: none; border-radius: 7px;
  padding: 5px 12px; font-size: 12px; font-weight: 600; cursor: pointer;
}
.btn-save:hover:not(:disabled) { background: #2563eb; }
.btn-save:disabled { opacity: 0.5; cursor: not-allowed; }

.comment-error {
  padding: 8px 12px; background: #fee2e2; color: #991b1b;
  border-radius: 7px; font-size: 12px;
}

/* Confirm overlay (kept inside this component) */
.cs-confirm-overlay {
  position: fixed; inset: 0; background: rgba(15, 23, 42, 0.5);
  z-index: 2100; display: flex; align-items: center; justify-content: center;
}
.cs-confirm {
  background: #fff; border-radius: 12px; padding: 20px 22px;
  max-width: 340px; width: 90%;
  box-shadow: 0 12px 40px rgba(0,0,0,0.18);
}
.cs-confirm h4 { margin: 0 0 6px; font-size: 15px; color: #1e293b; }
.cs-confirm p { margin: 0 0 16px; font-size: 13px; color: #475569; }
.cs-confirm-actions { display: flex; gap: 8px; justify-content: flex-end; }
.btn-danger-sm {
  background: #dc2626; color: #fff; border: none; border-radius: 7px;
  padding: 5px 14px; font-size: 12px; font-weight: 600; cursor: pointer;
}
.btn-danger-sm:hover:not(:disabled) { background: #b91c1c; }
.btn-danger-sm:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
