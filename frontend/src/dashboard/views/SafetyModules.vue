<template>
  <div class="modules-page">
    <div class="page-header">
      <div>
        <h2>Safety Modules</h2>
        <p>Complete all modules to stay up to date with workplace safety standards.</p>
      </div>
      <button v-if="isAdmin" class="btn-upload" @click="openUploadModal">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="17 8 12 3 7 8"/>
          <line x1="12" y1="3" x2="12" y2="15"/>
        </svg>
        Upload Module
      </button>
    </div>

    <div v-if="loading" class="state-msg">Loading modules...</div>
    <div v-else-if="error" class="state-msg error">{{ error }}</div>
    <div v-else-if="modules.length === 0" class="state-msg">No modules uploaded yet.</div>
    <div v-else class="modules-grid">
      <div v-for="mod in modules" :key="mod.id" class="module-card">
        <div class="card-thumb" @click="openWatchModal(mod)">
          <img
            v-if="mod.videoUrl"
            :src="thumbUrl(mod.videoUrl)"
            class="thumb-img"
            @error="e => e.target.style.display = 'none'"
          />
          <div class="thumb-overlay">
            <div class="play-btn">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <polygon points="6 4 20 12 6 20 6 4"/>
              </svg>
            </div>
          </div>
        </div>
        <div class="card-body">
          <div class="card-title">{{ mod.title }}</div>
          <div v-if="mod.description" class="card-desc">{{ mod.description }}</div>
        </div>
        <div class="card-footer">
          <button class="btn-watch" @click="openWatchModal(mod)">Watch</button>
          <button v-if="isAdmin" class="btn-delete" @click="confirmDelete(mod)" title="Delete">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3 6 5 6 21 6"/>
              <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
              <path d="M10 11v6M14 11v6"/>
              <path d="M9 6V4h6v2"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Upload Modal -->
    <div v-if="showUploadModal" class="modal-overlay" @click.self="closeUploadModal">
      <div class="modal">
        <div class="modal-header">
          <h3>Upload Module</h3>
          <button class="btn-close" @click="closeUploadModal">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Title <span class="req">*</span></label>
            <input v-model="uploadForm.title" type="text" placeholder="Module title" class="form-input" />
          </div>
          <div class="form-group">
            <label>Video File <span class="req">*</span></label>
            <div class="file-drop" @click="triggerFileInput" @dragover.prevent @drop.prevent="onFileDrop">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M15 10l4.553-2.069A1 1 0 0 1 21 8.83v6.34a1 1 0 0 1-1.447.899L15 14"/>
                <rect x="2" y="6" width="13" height="12" rx="2"/>
              </svg>
              <span v-if="uploadForm.file">{{ uploadForm.file.name }}</span>
              <span v-else>Click or drag a video file here</span>
            </div>
            <input ref="fileInputRef" type="file" accept="video/*" class="hidden-input" @change="onFileChange" />
          </div>
          <div class="form-group">
            <label>Description</label>
            <textarea v-model="uploadForm.description" placeholder="Optional description" class="form-input" rows="3"></textarea>
          </div>
          <div v-if="uploadError" class="form-error">{{ uploadError }}</div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="closeUploadModal" :disabled="uploading">Cancel</button>
          <button class="btn-submit" @click="submitUpload" :disabled="uploading">
            <span v-if="uploading">Uploading...</span>
            <span v-else>Upload</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Watch Modal -->
    <div v-if="watchingModule" class="modal-overlay" @click.self="closeWatchModal">
      <div class="modal modal-video">
        <div class="modal-header">
          <h3>{{ watchingModule.title }}</h3>
          <button class="btn-close" @click="closeWatchModal">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <video v-if="watchingModule.videoUrl" :src="watchingModule.videoUrl" controls class="video-player" />
          <p v-else class="state-msg">No video available.</p>
          <p v-if="watchingModule.description" class="video-desc">{{ watchingModule.description }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { authService } from "@/services/authService";
import { safetyModulesService, uploadVideo } from "@/services/safetyModulesService";

const user = authService.getCurrentUser();
const isAdmin = user?.roleId === 1;

const modules = ref([]);
const loading = ref(true);
const error = ref(null);

const showUploadModal = ref(false);
const uploading = ref(false);
const uploadError = ref(null);
const uploadForm = ref({ title: "", file: null, description: "" });
const fileInputRef = ref(null);

const watchingModule = ref(null);

async function fetchModules() {
  loading.value = true;
  error.value = null;
  try {
    modules.value = await safetyModulesService.list();
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}

onMounted(fetchModules);

function openUploadModal() {
  uploadForm.value = { title: "", file: null, description: "" };
  uploadError.value = null;
  showUploadModal.value = true;
}

function closeUploadModal() {
  if (!uploading.value) showUploadModal.value = false;
}

function triggerFileInput() {
  fileInputRef.value?.click();
}

function onFileChange(e) {
  uploadForm.value.file = e.target.files[0] || null;
}

function onFileDrop(e) {
  const file = e.dataTransfer.files[0];
  if (file && file.type.startsWith("video/")) {
    uploadForm.value.file = file;
  }
}

async function submitUpload() {
  uploadError.value = null;
  if (!uploadForm.value.title.trim()) {
    uploadError.value = "Title is required.";
    return;
  }
  if (!uploadForm.value.file) {
    uploadError.value = "Please select a video file.";
    return;
  }
  uploading.value = true;
  try {
    const videoUrl = await uploadVideo(uploadForm.value.file);
    await safetyModulesService.create(
      uploadForm.value.title.trim(),
      videoUrl,
      uploadForm.value.description.trim() || null,
    );
    showUploadModal.value = false;
    await fetchModules();
  } catch (e) {
    uploadError.value = e.message;
  } finally {
    uploading.value = false;
  }
}

async function confirmDelete(mod) {
  if (!confirm(`Delete module "${mod.title}"?`)) return;
  try {
    await safetyModulesService.delete(mod.id);
    await fetchModules();
  } catch (e) {
    alert(e.message);
  }
}

function thumbUrl(videoUrl) {
  // Cloudinary auto-generates a thumbnail by replacing the video extension with .jpg
  return videoUrl.replace(/\.(mp4|webm|mov|avi|mkv|flv|wmv)(\?.*)?$/i, ".jpg");
}

function openWatchModal(mod) {
  watchingModule.value = mod;
}

function closeWatchModal() {
  watchingModule.value = null;
}
</script>

<style scoped>
.modules-page {
  padding: 28px 32px;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 32px;
  gap: 16px;
  flex-wrap: wrap;
}

.page-header h2 {
  font-size: 22px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 6px;
}

.page-header p {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.btn-upload {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 9px 18px;
  background: #3b82f6;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
  flex-shrink: 0;
}

.btn-upload:hover { background: #2563eb; }

.btn-upload svg {
  width: 16px;
  height: 16px;
}

.state-msg {
  color: #64748b;
  font-size: 14px;
  padding: 32px 0;
  text-align: center;
}

.state-msg.error { color: #dc2626; }

.modules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 18px;
}

.module-card {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: box-shadow 0.2s, transform 0.2s;
}

.module-card:hover {
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

.card-thumb {
  height: 140px;
  background: #0f172a;
  position: relative;
  overflow: hidden;
  cursor: pointer;
}

.thumb-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.25s;
}

.card-thumb:hover .thumb-img {
  transform: scale(1.04);
}

.thumb-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.card-thumb:hover .thumb-overlay {
  background: rgba(0, 0, 0, 0.45);
}

.play-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.92);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #1e293b;
  transition: transform 0.2s, background 0.2s;
  box-shadow: 0 2px 12px rgba(0,0,0,0.3);
}

.card-thumb:hover .play-btn {
  transform: scale(1.1);
  background: #fff;
}

.play-btn svg {
  width: 18px;
  height: 18px;
  margin-left: 2px;
}

.card-body {
  padding: 14px 16px 8px;
  flex: 1;
}

.card-title {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  line-height: 1.4;
  margin-bottom: 4px;
}

.card-desc {
  font-size: 12px;
  color: #94a3b8;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  padding: 10px 16px 14px;
  display: flex;
  gap: 8px;
  align-items: center;
}

.btn-watch {
  flex: 1;
  padding: 8px;
  background: #3b82f6;
  color: #fff;
  border: none;
  border-radius: 7px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-watch:hover { background: #2563eb; }

.btn-delete {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  background: #fee2e2;
  color: #dc2626;
  border: none;
  border-radius: 7px;
  cursor: pointer;
  transition: background 0.15s;
  flex-shrink: 0;
}

.btn-delete:hover { background: #fecaca; }

.btn-delete svg { width: 15px; height: 15px; }

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
  padding: 16px;
}

.modal {
  background: #fff;
  border-radius: 14px;
  width: 100%;
  max-width: 480px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.2);
}

.modal-video {
  max-width: 720px;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px 16px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  font-size: 17px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.btn-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: none;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  color: #64748b;
  transition: background 0.15s;
}

.btn-close:hover { background: #f1f5f9; }
.btn-close svg { width: 18px; height: 18px; }

.modal-body {
  padding: 20px 24px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 6px;
}

.req { color: #dc2626; }

.form-input {
  width: 100%;
  padding: 9px 12px;
  border: 1px solid #d1d5db;
  border-radius: 7px;
  font-size: 14px;
  color: #1e293b;
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.15s;
  font-family: inherit;
}

.form-input:focus { border-color: #3b82f6; }

.file-drop {
  border: 2px dashed #d1d5db;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  color: #64748b;
  font-size: 13px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  transition: border-color 0.15s, background 0.15s;
}

.file-drop:hover {
  border-color: #3b82f6;
  background: #eff6ff;
}

.file-drop svg { width: 28px; height: 28px; color: #94a3b8; }

.hidden-input { display: none; }

.form-error {
  color: #dc2626;
  font-size: 13px;
  margin-top: 8px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 16px 24px 20px;
  border-top: 1px solid #e5e7eb;
}

.btn-cancel {
  padding: 9px 18px;
  background: #f1f5f9;
  color: #374151;
  border: none;
  border-radius: 7px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-cancel:hover:not(:disabled) { background: #e2e8f0; }

.btn-submit {
  padding: 9px 20px;
  background: #3b82f6;
  color: #fff;
  border: none;
  border-radius: 7px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-submit:hover:not(:disabled) { background: #2563eb; }
.btn-submit:disabled, .btn-cancel:disabled { opacity: 0.6; cursor: not-allowed; }

.video-player {
  width: 100%;
  border-radius: 8px;
  background: #000;
  max-height: 400px;
}

.video-desc {
  font-size: 13px;
  color: #64748b;
  margin: 12px 0 0;
}
</style>
