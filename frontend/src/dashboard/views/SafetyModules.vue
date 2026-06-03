<template>
  <div class="modules-page">
    <div class="page-header">
      <div>
        <h2>Safety Modules</h2>
        <p>Pelajari semua modul untuk selalu mengikuti standar keselamatan kerja.</p>
      </div>
      <button v-if="isAdmin" class="btn-upload" @click="openUploadModal">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="17 8 12 3 7 8"/>
          <line x1="12" y1="3" x2="12" y2="15"/>
        </svg>
        Unggah Modul
      </button>
    </div>

    <!-- Toolbar: filter first, search below -->
    <div class="toolbar">
      <div class="filter-tabs">
        <button
          class="filter-tab"
          :class="{ active: filterPeraturan === '' }"
          @click="filterPeraturan = ''"
        >Semua</button>
        <button
          v-for="opt in PERATURAN_OPTIONS"
          :key="opt"
          class="filter-tab"
          :class="{ active: filterPeraturan === opt }"
          @click="filterPeraturan = opt"
        >{{ opt }}</button>
      </div>
      <div class="search-wrap">
        <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          class="search-input"
          placeholder="Cari berdasarkan judul, peraturan, atau deskripsi..."
        />
        <button v-if="searchQuery" class="search-clear" @click="searchQuery = ''">✕</button>
      </div>
    </div>

    <div v-if="loading" class="state-msg">Memuat modul...</div>
    <div v-else-if="error" class="state-msg error">{{ error }}</div>
    <div v-else-if="modules.length === 0" class="state-msg">Belum ada modul yang diunggah.</div>
    <div v-else-if="filteredModules.length === 0" class="state-msg">Tidak ada modul yang cocok dengan pencarian.</div>
    <div v-else class="modules-grid">
      <div v-for="mod in filteredModules" :key="mod.id" class="module-card">
        <div class="card-thumb" @click="openViewModal(mod)">
          <!-- Video thumbnail -->
          <img
            v-if="primaryFile(mod).mediaType === 'video' && primaryFile(mod).url"
            :src="thumbUrl(primaryFile(mod).url)"
            class="thumb-img"
            @error="e => e.target.style.display = 'none'"
          />
          <!-- Image thumbnail -->
          <img
            v-else-if="primaryFile(mod).mediaType === 'image' && primaryFile(mod).url"
            :src="primaryFile(mod).url"
            class="thumb-img"
          />
          <!-- Document / no-media placeholder -->
          <div v-else class="thumb-placeholder">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="40" height="40">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="9" y1="13" x2="15" y2="13"/>
              <line x1="9" y1="17" x2="15" y2="17"/>
            </svg>
          </div>
          <div class="thumb-overlay">
            <div class="play-btn">
              <svg v-if="primaryFile(mod).mediaType === 'video'" viewBox="0 0 24 24" fill="currentColor">
                <polygon points="6 4 20 12 6 20 6 4"/>
              </svg>
              <svg v-else-if="primaryFile(mod).mediaType === 'image'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
              </svg>
            </div>
          </div>
          <!-- File count badge -->
          <span v-if="parseFiles(mod).length > 1" class="file-count-badge">{{ parseFiles(mod).length }} files</span>
          <!-- Primary media type badge -->
          <span class="media-badge" :class="`media-badge-${primaryFile(mod).mediaType}`">
            {{ primaryFile(mod).mediaType === 'image' ? 'Photo' : primaryFile(mod).mediaType === 'document' ? 'Doc' : 'Video' }}
          </span>
        </div>
        <div class="card-body">
          <div v-if="mod.peraturan" class="card-peraturan">{{ mod.peraturan }}</div>
          <div class="card-title">{{ mod.title }}</div>
          <div v-if="mod.description" class="card-desc">{{ mod.description }}</div>
        </div>
        <div class="card-footer">
          <button class="btn-watch" @click="openViewModal(mod)">
            {{ parseFiles(mod).length > 1 ? 'Buka' : primaryFile(mod).mediaType === 'image' ? 'Lihat' : primaryFile(mod).mediaType === 'document' ? 'Buka' : 'Tonton' }}
          </button>
          <button v-if="isAdmin" class="btn-edit" @click="openEditModal(mod)" title="Ubah">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
            </svg>
          </button>
          <button v-if="isAdmin" class="btn-delete" @click="confirmDelete(mod)" title="Hapus">
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
    <div v-if="showUploadModal" class="modal-overlay" @click.self="tryCloseUploadModal">
      <div class="modal">
        <div class="modal-header">
          <h3>Unggah Modul</h3>
          <button class="btn-close" @click="tryCloseUploadModal">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Judul <span class="req">*</span></label>
            <input v-model="uploadForm.title" type="text" placeholder="Judul modul" class="form-input" />
          </div>
          <div class="form-group">
            <label>Jenis Peraturan</label>
            <select v-model="uploadForm.peraturan" class="form-input">
              <option value="">— Pilih jenis peraturan —</option>
              <option value="Peraturan Dinas">Peraturan Dinas</option>
              <option value="Peraturan Daerah">Peraturan Daerah</option>
              <option value="Peraturan Pemerintah">Peraturan Pemerintah</option>
              <option value="Peraturan Skala Nasional">Peraturan Skala Nasional</option>
              <option value="Peraturan Skala Internasional">Peraturan Skala Internasional</option>
            </select>
          </div>
          <div class="form-group">
            <label>File <span class="req">*</span></label>
            <div class="file-drop" @click="triggerFileInput" @dragover.prevent @drop.prevent="onFileDrop">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="17 8 12 3 7 8"/>
                <line x1="12" y1="3" x2="12" y2="15"/>
              </svg>
              <span v-if="uploadForm.files.length === 0">
                Klik atau seret file ke sini<br/>
                <small>Boleh banyak file — video, foto, atau dokumen (PDF, Word, Excel, PowerPoint)</small>
              </span>
              <span v-else>{{ uploadForm.files.length }} file dipilih</span>
            </div>
            <input
              ref="fileInputRef"
              type="file"
              accept="video/*,image/*,.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx"
              multiple
              class="hidden-input"
              @change="onFileChange"
            />
            <!-- File list -->
            <ul v-if="uploadForm.files.length" class="file-list">
              <li v-for="(f, i) in uploadForm.files" :key="i" class="file-list-item">
                <span class="file-type-chip" :class="`chip-${getMediaType(f)}`">{{ getMediaType(f) }}</span>
                <span class="file-name">{{ f.name }}</span>
                <button class="file-remove" @click="removeFile(i)">✕</button>
              </li>
            </ul>
          </div>
          <div class="form-group">
            <label>Deskripsi</label>
            <textarea v-model="uploadForm.description" placeholder="Deskripsi (opsional)" class="form-input" rows="3"></textarea>
          </div>
          <div v-if="uploadError" class="form-error">{{ uploadError }}</div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="tryCloseUploadModal" :disabled="uploading">Batal</button>
          <button class="btn-submit" @click="submitUpload" :disabled="uploading">
            <span v-if="uploading">Mengunggah...</span>
            <span v-else>Unggah</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Discard Confirm Dialog -->
    <div v-if="showDiscardConfirm" class="modal-overlay" style="z-index:1001">
      <div class="modal modal-confirm">
        <div class="modal-body" style="padding:28px 24px 20px">
          <div class="confirm-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/>
              <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
          </div>
          <h4 class="confirm-title">Batalkan perubahan?</h4>
          <p class="confirm-desc">Anda memiliki data yang belum disimpan. Apakah yakin ingin menutup form ini?</p>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="showDiscardConfirm = false">Kembali</button>
          <button class="btn-discard" @click="forceClose">Ya, Batalkan</button>
        </div>
      </div>
    </div>

    <!-- Delete Confirm Modal -->
    <div v-if="deletingModule" class="modal-overlay" style="z-index:1001">
      <div class="modal modal-confirm">
        <div class="modal-body" style="padding:32px 28px 20px">
          <div class="confirm-icon confirm-icon-danger">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <polyline points="3 6 5 6 21 6"/>
              <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
              <path d="M10 11v6M14 11v6"/>
              <path d="M9 6V4h6v2"/>
            </svg>
          </div>
          <h4 class="confirm-title">Hapus Modul?</h4>
          <p class="confirm-desc">
            Anda akan menghapus modul<br/>
            <strong>"{{ deletingModule.title }}"</strong><br/>
            Tindakan ini tidak dapat dibatalkan.
          </p>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="deletingModule = null" :disabled="deleting">Batal</button>
          <button class="btn-discard" @click="executeDelete" :disabled="deleting">
            <span v-if="deleting">Menghapus...</span>
            <span v-else>Ya, Hapus</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Edit Discard Confirm Dialog -->
    <div v-if="showEditDiscardConfirm" class="modal-overlay" style="z-index:1002">
      <div class="modal modal-confirm">
        <div class="modal-body" style="padding:28px 24px 20px">
          <div class="confirm-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/>
              <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
          </div>
          <h4 class="confirm-title">Batalkan perubahan?</h4>
          <p class="confirm-desc">Perubahan yang belum disimpan akan hilang. Apakah yakin ingin menutup form ini?</p>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="showEditDiscardConfirm = false">Kembali</button>
          <button class="btn-discard" @click="forceCloseEdit">Ya, Batalkan</button>
        </div>
      </div>
    </div>

    <!-- Edit Modal -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="tryCloseEditModal">
      <div class="modal">
        <div class="modal-header">
          <h3>Ubah Modul</h3>
          <button class="btn-close" @click="closeEditModal">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Judul <span class="req">*</span></label>
            <input v-model="editForm.title" type="text" placeholder="Judul modul" class="form-input" />
          </div>
          <div class="form-group">
            <label>Jenis Peraturan</label>
            <select v-model="editForm.peraturan" class="form-input">
              <option value="">— Pilih jenis peraturan —</option>
              <option v-for="opt in PERATURAN_OPTIONS" :key="opt" :value="opt">{{ opt }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>Deskripsi</label>
            <textarea v-model="editForm.description" placeholder="Deskripsi (opsional)" class="form-input" rows="3"></textarea>
          </div>
          <!-- Existing files -->
          <div class="form-group" v-if="editForm.existingFiles.length">
            <label>File Saat Ini</label>
            <ul class="file-list">
              <li v-for="(f, i) in editForm.existingFiles" :key="i" class="file-list-item">
                <span class="file-type-chip" :class="`chip-${f.mediaType}`">{{ f.mediaType }}</span>
                <span class="file-name">{{ f.name }}</span>
                <button class="file-remove" @click="removeExistingFile(i)" title="Hapus">✕</button>
              </li>
            </ul>
          </div>
          <!-- Add new files -->
          <div class="form-group">
            <label>Tambah File Baru</label>
            <div class="file-drop" @click="triggerEditFileInput" @dragover.prevent @drop.prevent="onEditFileDrop">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="17 8 12 3 7 8"/>
                <line x1="12" y1="3" x2="12" y2="15"/>
              </svg>
              <span v-if="editForm.newFiles.length === 0">
                Klik atau seret untuk menambah file<br/>
                <small>Video, foto, atau dokumen (PDF, Word, Excel, PowerPoint)</small>
              </span>
              <span v-else>{{ editForm.newFiles.length }} file baru dipilih</span>
            </div>
            <input
              ref="editFileInputRef"
              type="file"
              accept="video/*,image/*,.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx"
              multiple
              class="hidden-input"
              @change="onEditFileChange"
            />
            <ul v-if="editForm.newFiles.length" class="file-list" style="margin-top:8px">
              <li v-for="(f, i) in editForm.newFiles" :key="i" class="file-list-item">
                <span class="file-type-chip" :class="`chip-${getMediaType(f)}`">{{ getMediaType(f) }}</span>
                <span class="file-name">{{ f.name }}</span>
                <button class="file-remove" @click="removeNewFile(i)">✕</button>
              </li>
            </ul>
          </div>
          <div v-if="editError" class="form-error">{{ editError }}</div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="closeEditModal" :disabled="editSaving">Batal</button>
          <button class="btn-submit" @click="submitEdit" :disabled="editSaving">
            <span v-if="editSaving">Menyimpan...</span>
            <span v-else>Simpan Perubahan</span>
          </button>
        </div>
      </div>
    </div>

    <!-- View Modal (video / image / document) -->
    <div v-if="viewingModule" class="modal-overlay" @click.self="closeViewModal">
      <div class="modal modal-view-wide">
        <div class="modal-header">
          <h3>{{ viewingModule.title }}</h3>
          <button class="btn-close" @click="closeViewModal">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <div class="modal-body modal-body-scroll">
          <div v-if="parseFiles(viewingModule).length" class="files-viewer">
            <div v-for="(f, i) in parseFiles(viewingModule)" :key="i" class="file-block">
              <div class="file-block-label">
                <span class="file-type-chip" :class="`chip-${f.mediaType}`">{{ f.mediaType }}</span>
                <span class="file-block-name">{{ f.name }}</span>
                <button class="btn-dl" @click="downloadFile(f.url, f.name)" title="Download">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                    <polyline points="7 10 12 15 17 10"/>
                    <line x1="12" y1="15" x2="12" y2="3"/>
                  </svg>
                  Unduh
                </button>
              </div>
              <!-- Video -->
              <video v-if="f.mediaType === 'video'" :src="f.url" controls class="video-player" />
              <!-- Image — click to open lightbox -->
              <img
                v-else-if="f.mediaType === 'image'"
                :src="f.url"
                class="image-viewer image-clickable"
                @click="openLightbox(f.url)"
                title="Klik untuk memperbesar"
              />
              <!-- Document: open in new tab (PDF uses browser PDF viewer) -->
              <div v-else class="doc-preview">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="40" height="40">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                  <line x1="9" y1="13" x2="15" y2="13"/>
                  <line x1="9" y1="17" x2="15" y2="17"/>
                </svg>
                <button v-if="isPdf(f)" class="btn-open-doc" @click="openPdf(f.url)">
                  Buka PDF
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                    <polyline points="15 3 21 3 21 9"/>
                    <line x1="10" y1="14" x2="21" y2="3"/>
                  </svg>
                </button>
                <a v-else :href="f.url" target="_blank" rel="noopener" class="btn-open-doc">
                  Buka Dokumen
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                    <polyline points="15 3 21 3 21 9"/>
                    <line x1="10" y1="14" x2="21" y2="3"/>
                  </svg>
                </a>
              </div>
            </div>
          </div>
          <p v-else class="state-msg">Tidak ada file tersedia.</p>
          <div v-if="viewingModule.peraturan" class="view-peraturan">{{ viewingModule.peraturan }}</div>
          <p v-if="viewingModule.description" class="media-desc">{{ viewingModule.description }}</p>
        </div>
      </div>
    </div>

    <!-- Image Lightbox -->
    <div v-if="lightboxImg" class="lightbox-overlay" @click="lightboxImg = null">
      <button class="lightbox-close" @click="lightboxImg = null">✕</button>
      <img :src="lightboxImg" class="lightbox-img" @click.stop />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { authService } from "@/services/authService";
import { safetyModulesService, uploadFile, getMediaType } from "@/services/safetyModulesService";

const user = authService.getCurrentUser();
const isAdmin = user?.roleId === 1;

const modules = ref([]);
const loading = ref(true);
const error = ref(null);

const showUploadModal = ref(false);
const uploading = ref(false);
const uploadError = ref(null);
const uploadForm = ref({ title: "", files: [], peraturan: "", description: "" });
const fileInputRef = ref(null);
const showDiscardConfirm = ref(false);

const viewingModule = ref(null);

const PERATURAN_OPTIONS = [
  "Peraturan Dinas",
  "Peraturan Daerah",
  "Peraturan Pemerintah",
  "Peraturan Skala Nasional",
  "Peraturan Skala Internasional",
];

const searchQuery = ref("");
const filterPeraturan = ref("");

const filteredModules = computed(() => {
  const q = searchQuery.value.trim().toLowerCase();
  const p = filterPeraturan.value;
  return modules.value.filter((mod) => {
    if (p && mod.peraturan !== p) return false;
    if (!q) return true;
    return (
      mod.title?.toLowerCase().includes(q) ||
      mod.peraturan?.toLowerCase().includes(q) ||
      mod.description?.toLowerCase().includes(q)
    );
  });
});

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
  uploadForm.value = { title: "", files: [], peraturan: "", description: "" };
  uploadError.value = null;
  showDiscardConfirm.value = false;
  showUploadModal.value = true;
}

function hasUploadChanges() {
  return !!(uploadForm.value.title.trim() || uploadForm.value.files.length || uploadForm.value.description.trim());
}

function tryCloseUploadModal() {
  if (uploading.value) return;
  if (hasUploadChanges()) {
    showDiscardConfirm.value = true;
  } else {
    showUploadModal.value = false;
  }
}

function forceClose() {
  showDiscardConfirm.value = false;
  showUploadModal.value = false;
}

function triggerFileInput() {
  fileInputRef.value?.click();
}

function onFileChange(e) {
  const incoming = Array.from(e.target.files);
  uploadForm.value.files = [...uploadForm.value.files, ...incoming];
  e.target.value = "";
}

function onFileDrop(e) {
  const incoming = Array.from(e.dataTransfer.files);
  uploadForm.value.files = [...uploadForm.value.files, ...incoming];
}

function removeFile(index) {
  uploadForm.value.files.splice(index, 1);
}

async function submitUpload() {
  uploadError.value = null;
  if (!uploadForm.value.title.trim()) {
    uploadError.value = "Judul wajib diisi.";
    return;
  }
  if (!uploadForm.value.files.length) {
    uploadError.value = "Harap pilih minimal satu file.";
    return;
  }
  uploading.value = true;
  try {
    const uploaded = await Promise.all(uploadForm.value.files.map(async (f) => {
      const { url, mediaType } = await uploadFile(f);
      return { url, mediaType, name: f.name };
    }));
    await safetyModulesService.create(
      uploadForm.value.title.trim(),
      uploaded,
      uploadForm.value.description.trim() || null,
      uploadForm.value.peraturan || null,
    );
    showUploadModal.value = false;
    await fetchModules();
  } catch (e) {
    uploadError.value = e.message;
  } finally {
    uploading.value = false;
  }
}

function parseFiles(mod) {
  if (mod.files) {
    try { return JSON.parse(mod.files); } catch { /* fall through */ }
  }
  if (mod.videoUrl) return [{ url: mod.videoUrl, mediaType: mod.mediaType || "video", name: mod.title }];
  return [];
}

function primaryFile(mod) {
  const files = parseFiles(mod);
  return files[0] ?? { url: null, mediaType: "document", name: "" };
}

const deletingModule = ref(null);
const deleting = ref(false);

function confirmDelete(mod) {
  deletingModule.value = mod;
}

async function executeDelete() {
  if (!deletingModule.value) return;
  deleting.value = true;
  try {
    await safetyModulesService.delete(deletingModule.value.id);
    deletingModule.value = null;
    await fetchModules();
  } catch (e) {
    alert(e.message);
  } finally {
    deleting.value = false;
  }
}

function thumbUrl(videoUrl) {
  return videoUrl.replace(/\.(mp4|webm|mov|avi|mkv|flv|wmv)(\?.*)?$/i, ".jpg");
}

function openViewModal(mod) {
  viewingModule.value = mod;
}

function closeViewModal() {
  viewingModule.value = null;
}

function isPdf(f) {
  return f.name?.toLowerCase().endsWith(".pdf") || f.url?.toLowerCase().includes(".pdf");
}

async function openPdf(url) {
  try {
    const res = await fetch(url);
    const blob = await res.blob();
    const blobUrl = URL.createObjectURL(new Blob([blob], { type: "application/pdf" }));
    const tab = window.open(blobUrl, "_blank");
    // revoke after the tab has had time to load
    setTimeout(() => URL.revokeObjectURL(blobUrl), 30000);
    if (!tab) window.location.href = blobUrl; // popup blocked fallback
  } catch {
    window.open(url, "_blank");
  }
}

async function downloadFile(url, name) {
  try {
    const res = await fetch(url);
    const blob = await res.blob();
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = name || "download";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(a.href);
  } catch {
    window.open(url, "_blank");
  }
}

const lightboxImg = ref(null);

function openLightbox(url) {
  lightboxImg.value = url;
}

// ── Edit modal ───────────────────────────────────────────────────────────────

const showEditModal = ref(false);
const editSaving = ref(false);
const editError = ref(null);
const editingId = ref(null);
const editFileInputRef = ref(null);
const editForm = ref({ title: "", peraturan: "", description: "", existingFiles: [], newFiles: [] });

function openEditModal(mod) {
  editingId.value = mod.id;
  editForm.value = {
    title: mod.title,
    peraturan: mod.peraturan || "",
    description: mod.description || "",
    existingFiles: parseFiles(mod).map((f) => ({ ...f })),
    newFiles: [],
  };
  editError.value = null;
  showEditModal.value = true;
}

const showEditDiscardConfirm = ref(false);

function hasEditChanges() {
  const mod = modules.value.find((m) => m.id === editingId.value);
  if (!mod) return false;
  if (editForm.value.title !== mod.title) return true;
  if (editForm.value.peraturan !== (mod.peraturan || "")) return true;
  if (editForm.value.description !== (mod.description || "")) return true;
  if (editForm.value.newFiles.length > 0) return true;
  const orig = parseFiles(mod);
  if (editForm.value.existingFiles.length !== orig.length) return true;
  return false;
}

function tryCloseEditModal() {
  if (editSaving.value) return;
  if (hasEditChanges()) {
    showEditDiscardConfirm.value = true;
  } else {
    showEditModal.value = false;
  }
}

function forceCloseEdit() {
  showEditDiscardConfirm.value = false;
  showEditModal.value = false;
}

function closeEditModal() {
  tryCloseEditModal();
}

function removeExistingFile(i) {
  editForm.value.existingFiles.splice(i, 1);
}

function triggerEditFileInput() {
  editFileInputRef.value?.click();
}

function onEditFileChange(e) {
  editForm.value.newFiles = [...editForm.value.newFiles, ...Array.from(e.target.files)];
  e.target.value = "";
}

function onEditFileDrop(e) {
  editForm.value.newFiles = [...editForm.value.newFiles, ...Array.from(e.dataTransfer.files)];
}

function removeNewFile(i) {
  editForm.value.newFiles.splice(i, 1);
}

async function submitEdit() {
  editError.value = null;
  if (!editForm.value.title.trim()) {
    editError.value = "Judul wajib diisi.";
    return;
  }
  if (editForm.value.existingFiles.length === 0 && editForm.value.newFiles.length === 0) {
    editError.value = "Minimal satu file wajib ada.";
    return;
  }
  editSaving.value = true;
  try {
    const uploaded = await Promise.all(editForm.value.newFiles.map(async (f) => {
      const { url, mediaType } = await uploadFile(f);
      return { url, mediaType, name: f.name };
    }));
    const allFiles = [...editForm.value.existingFiles, ...uploaded];
    await safetyModulesService.update(
      editingId.value,
      editForm.value.title.trim(),
      allFiles,
      editForm.value.description.trim(),
      editForm.value.peraturan,
    );
    showEditModal.value = false;
    await fetchModules();
  } catch (e) {
    editError.value = e.message;
  } finally {
    editSaving.value = false;
  }
}
</script>

<style scoped>
.modules-page {
  padding: 28px 32px;
}
@media (max-width: 1024px) { .modules-page { padding: 20px 20px; } }
@media (max-width: 640px)  { .modules-page { padding: 16px 14px; } }

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
  margin: 0 0 4px;
}

.page-header p {
  font-size: 13px;
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

.toolbar {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
}

.search-wrap {
  position: relative;
  width: 100%;
}

.search-icon {
  position: absolute;
  left: 11px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  color: #94a3b8;
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 9px 36px 9px 36px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  color: #1e293b;
  background: #fff;
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.15s;
}

.search-input:focus { border-color: #3b82f6; }
.search-input::placeholder { color: #94a3b8; }

.search-clear {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  color: #94a3b8;
  font-size: 12px;
  padding: 2px 4px;
  line-height: 1;
}

.search-clear:hover { color: #ef4444; }

.filter-tabs {
  display: flex;
  gap: 8px;
  flex-wrap: nowrap;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  padding-bottom: 2px;
}

.filter-tabs::-webkit-scrollbar {
  display: none;
}

.filter-tab {
  padding: 6px 14px;
  border: 1px solid #e5e7eb;
  border-radius: 999px;
  background: #fff;
  font-size: 12px;
  font-weight: 500;
  color: #64748b;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s, color 0.15s;
  white-space: nowrap;
  flex-shrink: 0;
}

.filter-tab:hover { border-color: #3b82f6; color: #3b82f6; }
.filter-tab.active { background: #3b82f6; border-color: #3b82f6; color: #fff; font-weight: 600; }

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

.thumb-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1e293b;
  color: #475569;
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

.media-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  font-size: 10px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 999px;
  text-transform: uppercase;
  letter-spacing: 0.4px;
}

.media-badge-video { background: #1e293b; color: #94a3b8; }
.media-badge-image { background: #7c3aed; color: #fff; }
.media-badge-document { background: #0284c7; color: #fff; }

.card-body {
  padding: 14px 16px 8px;
  flex: 1;
}

.card-peraturan {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #3b82f6;
  margin-bottom: 4px;
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

.btn-edit {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  background: #eff6ff;
  color: #3b82f6;
  border: none;
  border-radius: 7px;
  cursor: pointer;
  transition: background 0.15s;
  flex-shrink: 0;
}

.btn-edit:hover { background: #dbeafe; }
.btn-edit svg { width: 15px; height: 15px; }

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

.modal-video { max-width: 720px; }
.modal-view  { max-width: 640px; }

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
  background: #fff;
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
.file-drop small { color: #94a3b8; margin-top: 2px; }

.file-list {
  list-style: none;
  margin: 8px 0 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.file-list-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: #f8fafc;
  border: 1px solid #e5e7eb;
  border-radius: 7px;
  font-size: 13px;
}

.file-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #374151;
}

.file-remove {
  background: none;
  border: none;
  cursor: pointer;
  color: #94a3b8;
  font-size: 12px;
  padding: 2px 4px;
  border-radius: 4px;
  flex-shrink: 0;
  transition: color 0.15s;
}

.file-remove:hover { color: #ef4444; }

.file-count-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  font-size: 10px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 999px;
  background: rgba(0,0,0,0.55);
  color: #fff;
}

.files-viewer {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.file-block {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.file-block-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-block-name {
  font-size: 13px;
  color: #64748b;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-type-chip {
  display: inline-block;
  margin-left: 8px;
  font-size: 10px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 999px;
  text-transform: uppercase;
  vertical-align: middle;
}

.chip-video    { background: #1e293b; color: #94a3b8; }
.chip-image    { background: #7c3aed; color: #fff; }
.chip-document { background: #0284c7; color: #fff; }

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

.image-viewer {
  width: 100%;
  border-radius: 8px;
  object-fit: contain;
  max-height: 480px;
  display: block;
}

.doc-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 24px 0 8px;
  color: #64748b;
}

.doc-preview p {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
  text-align: center;
}

.btn-open-doc {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  background: #0284c7;
  color: #fff;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  transition: background 0.15s;
}

.btn-open-doc:hover { background: #0369a1; }

.modal-confirm {
  max-width: 360px;
}

.confirm-icon {
  display: flex;
  justify-content: center;
  margin-bottom: 16px;
}

.confirm-icon svg {
  width: 44px;
  height: 44px;
  color: #f59e0b;
}

.confirm-icon-danger {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: #fef2f2;
  margin: 0 auto 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.confirm-icon-danger svg {
  width: 32px;
  height: 32px;
  color: #ef4444;
}

.confirm-title {
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
  text-align: center;
  margin: 0 0 8px;
}

.confirm-desc {
  font-size: 13px;
  color: #64748b;
  text-align: center;
  margin: 0;
  line-height: 1.6;
}

.btn-discard {
  padding: 9px 18px;
  background: #ef4444;
  color: #fff;
  border: none;
  border-radius: 7px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-discard:hover { background: #dc2626; }

.view-peraturan {
  display: inline-block;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #3b82f6;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 6px;
  padding: 3px 10px;
  margin-bottom: 12px;
}

.media-desc {
  font-size: 13px;
  color: #64748b;
  margin: 12px 0 0;
}

/* Wide view modal */
.modal-view-wide { max-width: 860px; }

.modal-body-scroll {
  max-height: 72vh;
  overflow-y: auto;
}

/* Download button in file-block-label */
.file-block-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-dl {
  margin-left: auto;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 10px;
  background: #f1f5f9;
  color: #374151;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  text-decoration: none;
  white-space: nowrap;
  transition: background 0.15s;
  flex-shrink: 0;
}

.btn-dl:hover { background: #e2e8f0; }

/* Image viewer — click to zoom */
.image-clickable {
  cursor: zoom-in;
  transition: opacity 0.15s;
}

.image-clickable:hover { opacity: 0.9; }

/* Lightbox */
.lightbox-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.92);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: zoom-out;
}

.lightbox-img {
  max-width: 95vw;
  max-height: 90vh;
  object-fit: contain;
  border-radius: 6px;
  box-shadow: 0 8px 48px rgba(0,0,0,0.6);
  cursor: default;
}

.lightbox-close {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
  border: none;
  color: #fff;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
  z-index: 1;
}

.lightbox-close:hover { background: rgba(255, 255, 255, 0.28); }
</style>
