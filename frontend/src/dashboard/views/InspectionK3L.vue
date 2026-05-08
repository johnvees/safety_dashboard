<template>
  <div class="inspection-k3l">
    <div class="page-header">
      <h2>Inspection K3L</h2>
      <p class="subtitle">
        Keselamatan, Kesehatan Kerja & Lingkungan inspection reports
      </p>
    </div>

    <!-- Action bar -->
    <div class="action-bar">
      <button class="btn btn-primary" @click="showForm = true" v-if="!showForm">
        + Tambah Temuan
      </button>
      <button class="btn btn-secondary" @click="cancelForm" v-if="showForm">
        Batal
      </button>
    </div>

    <!-- Input Form -->
    <div class="form-card" v-if="showForm">
      <h3 class="form-title">
        {{ editingId ? 'Edit Temuan' : 'Input Temuan Baru' }}
      </h3>
      <form @submit.prevent="submitForm" class="form-grid">
        <!-- Waktu -->
        <div class="form-section">
          <h4 class="section-title">Waktu</h4>
          <div class="form-row">
            <div class="form-group">
              <label>Tanggal <span class="required">*</span></label>
              <div class="date-input-wrapper">
                <input
                  type="date"
                  v-model="form.tanggal"
                  required
                  ref="tanggalInput"
                />
                <svg
                  class="date-icon"
                  @click="$refs.tanggalInput.showPicker()"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  width="18"
                  height="18"
                >
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                  <line x1="16" y1="2" x2="16" y2="6" />
                  <line x1="8" y1="2" x2="8" y2="6" />
                  <line x1="3" y1="10" x2="21" y2="10" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        <!-- Temuan -->
        <div class="form-section">
          <h4 class="section-title">Temuan</h4>
          <div class="form-row">
            <div class="form-group">
              <label>Kategori Temuan <span class="required">*</span></label>
              <select v-model="form.kategoriTemuan" required>
                <option value="" disabled>Pilih Kategori</option>
                <option value="Unsafe Action">Unsafe Action</option>
                <option value="Unsafe Condition">Unsafe Condition</option>
                <option value="Lingkungan">Lingkungan</option>
                <option value="Kesehatan Kerja">Kesehatan Kerja</option>
                <option value="APD">APD</option>
                <option value="Housekeeping">Housekeeping</option>
                <option value="Lainnya">Lainnya</option>
              </select>
            </div>
            <div class="form-group full-width">
              <label>Deskripsi Temuan</label>
              <textarea
                v-model="form.deskripsiTemuan"
                rows="3"
                placeholder="Jelaskan temuan secara detail..."
              ></textarea>
            </div>
          </div>
        </div>

        <!-- Foto -->
        <div class="form-section">
          <h4 class="section-title">Foto</h4>
          <div class="form-row">
            <div class="form-group full-width">
              <label
                >Foto Temuan
                <span class="photo-count">({{ photos.length }}/10)</span></label
              >
              <div class="photo-upload">
                <div class="photo-grid" v-if="photos.length > 0">
                  <div
                    class="photo-preview"
                    v-for="(photo, idx) in photos"
                    :key="idx"
                  >
                    <img :src="photo.preview" alt="Preview" />
                    <button
                      type="button"
                      class="photo-remove"
                      @click="removePhotoAt(idx)"
                    >
                      x
                    </button>
                  </div>
                </div>
                <div class="photo-clear" v-if="photos.length > 1">
                  <button type="button" class="btn btn-clear" @click="clearPhotos">
                    Hapus Semua Foto
                  </button>
                </div>
                <div class="photo-actions" v-if="photos.length < 10">
                  <label class="photo-btn">
                    <svg
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                      width="20"
                      height="20"
                    >
                      <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                      <circle cx="8.5" cy="8.5" r="1.5" />
                      <polyline points="21 15 16 10 5 21" />
                    </svg>
                    Galeri
                    <input
                      type="file"
                      accept="image/*"
                      multiple
                      @change="onPhotoSelect"
                      hidden
                    />
                  </label>
                  <label class="photo-btn">
                    <svg
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                      width="20"
                      height="20"
                    >
                      <path
                        d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"
                      />
                      <circle cx="12" cy="13" r="4" />
                    </svg>
                    Kamera
                    <input
                      type="file"
                      accept="image/*"
                      capture="environment"
                      @change="onPhotoSelect"
                      hidden
                    />
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Lokasi -->
        <div class="form-section">
          <h4 class="section-title">Lokasi</h4>
          <div class="form-row">
            <div class="form-group form-group-fill">
              <label>Lokasi</label>
              <input
                type="text"
                v-model="form.lokasi"
                placeholder="Lokasi temuan"
              />
            </div>
            <div class="form-group form-group-fill">
              <label>Business Unit</label>
              <select v-model.number="form.businessUnitId" @change="onBusinessUnitChange">
                <option :value="null">Pilih Business Unit</option>
                <option v-for="unit in businessUnits" :key="unit.id" :value="unit.id">
                  {{ unit.name }}
                </option>
              </select>
            </div>
            <div class="form-group form-group-fill">
              <label>Plant</label>
              <select v-model.number="form.plantId" :disabled="!form.businessUnitId">
                <option :value="null">Pilih Plant</option>
                <option v-for="plant in filteredPlants" :key="plant.id" :value="plant.id">
                  {{ plant.name }}
                </option>
              </select>
            </div>
          </div>
        </div>

        <!-- Tindakan -->
        <div class="form-section">
          <h4 class="section-title">Tindakan</h4>
          <div class="form-row">
            <div class="form-group full-width">
              <label>Tindakan Perbaikan</label>
              <textarea
                v-model="form.tindakanPerbaikan"
                rows="3"
                placeholder="Jelaskan tindakan perbaikan yang dilakukan..."
              ></textarea>
            </div>
            <div class="form-group">
              <label>Target Selesai</label>
              <div class="date-input-wrapper">
                <input
                  type="date"
                  v-model="form.targetSelesai"
                  ref="targetSelesaiInput"
                />
                <svg
                  class="date-icon"
                  @click="$refs.targetSelesaiInput.showPicker()"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  width="18"
                  height="18"
                >
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                  <line x1="16" y1="2" x2="16" y2="6" />
                  <line x1="8" y1="2" x2="8" y2="6" />
                  <line x1="3" y1="10" x2="21" y2="10" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        <!-- Status -->
        <div class="form-section">
          <h4 class="section-title">Status</h4>
          <div class="form-row">
            <div class="form-group">
              <label>Status</label>
              <select v-model="form.status" :disabled="!editingId">
                <option value="Open">Open</option>
                <option value="In Progress">In Progress</option>
                <option value="Closed">Closed</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Submit -->
        <div class="form-actions">
          <button type="submit" class="btn btn-primary" :disabled="submitting">
            {{ submitting ? 'Menyimpan...' : editingId ? 'Update' : 'Simpan' }}
          </button>
          <button type="button" class="btn btn-secondary" @click="cancelForm">
            Batal
          </button>
        </div>
      </form>
    </div>

    <!-- Toast notification -->
    <Teleport to="body">
      <Transition name="toast">
        <div v-if="toast.show" :class="['toast', `toast-${toast.type}`]">
          <span class="toast-text">{{ toast.message }}</span>
          <button class="toast-close" @click="toast.show = false">x</button>
        </div>
      </Transition>
    </Teleport>

    <!-- Data Table -->
    <div class="table-card">
      <div class="table-header">
        <h3>Data Temuan</h3>
        <button class="btn btn-sm" @click="loadData" :disabled="loading">
          {{ loading ? 'Loading...' : 'Refresh' }}
        </button>
      </div>
      <div class="table-wrapper">
        <table v-if="records.length > 0">
          <thead>
            <tr>
              <th>No</th>
              <th>Tanggal</th>
              <th>Kategori</th>
              <th>Deskripsi</th>
              <th>Lokasi</th>
              <th>Status</th>
              <th>Target Selesai</th>
              <th>Aksi</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, idx) in records" :key="item.id">
              <td>{{ idx + 1 }}</td>
              <td>{{ item.tanggal }}</td>
              <td>{{ item.kategoriTemuan }}</td>
              <td class="td-desc">{{ item.deskripsiTemuan || '-' }}</td>
              <td>{{ item.lokasi || '-' }}</td>
              <td>
                <span
                  :class="[
                    'status-badge',
                    `status-${item.status.toLowerCase().replace(' ', '-')}`,
                  ]"
                >
                  {{ item.status }}
                </span>
              </td>
              <td>{{ item.targetSelesai || '-' }}</td>
              <td class="td-actions">
                <button class="btn-icon" title="Edit" @click="editRecord(item)">
                  <svg
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    width="16"
                    height="16"
                  >
                    <path
                      d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"
                    />
                    <path
                      d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"
                    />
                  </svg>
                </button>
                <button
                  class="btn-icon btn-danger"
                  title="Hapus"
                  @click="deleteRecord(item.id)"
                >
                  <svg
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    width="16"
                    height="16"
                  >
                    <polyline points="3 6 5 6 21 6" />
                    <path
                      d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"
                    />
                  </svg>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-else class="empty-state">
          <p>Belum ada data temuan. Klik "Tambah Temuan" untuk menambahkan.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { inspectionK3LService, uploadImage } from '@/services/inspectionK3LService.js';

const showForm = ref(false);
const submitting = ref(false);
const loading = ref(false);
const editingId = ref(null);
const records = ref([]);
const businessUnits = ref([]);
const plants = ref([]);

const filteredPlants = computed(() => {
  if (!form.value.businessUnitId) return [];
  return plants.value.filter((plant) => plant.businessUnitId === form.value.businessUnitId);
});

// Toast notification
const toast = reactive({ show: false, message: '', type: 'success' });
let toastTimer = null;

function showToast(msg, type = 'success') {
  if (type === 'error') {
    console.error(msg);
    return;
  }

  if (toastTimer) clearTimeout(toastTimer);
  toast.show = true;
  toast.message = msg;
  toast.type = type;
  toastTimer = setTimeout(() => {
    toast.show = false;
  }, 4000);
}

// Photo handling - multiple photos, max 10
const photos = ref([]); // Array of { file, preview }

function onPhotoSelect(event) {
  const files = Array.from(event.target.files);
  if (!files.length) return;

  const remaining = 10 - photos.value.length;

  // Cancel entirely if user tries to add more than allowed
  if (files.length > remaining) {
    event.target.value = '';
    showToast(
      `Maksimal 10 foto. Anda hanya dapat menambahkan ${remaining} foto lagi. Silakan pilih ulang.`,
      'warning',
    );
    return;
  }

  for (const file of files) {
    photos.value.push({
      file,
      preview: URL.createObjectURL(file),
    });
  }

  // Reset input so same file can be re-selected
  event.target.value = '';
}

function removePhotoAt(idx) {
  const photo = photos.value[idx];
  if (photo.preview && photo.preview.startsWith('blob:')) {
    URL.revokeObjectURL(photo.preview);
  }
  photos.value.splice(idx, 1);
}

function clearPhotos() {
  photos.value.forEach((p) => {
    if (p.preview && p.preview.startsWith('blob:')) {
      URL.revokeObjectURL(p.preview);
    }
  });
  photos.value = [];
}

const defaultForm = () => ({
  tanggal: '',
  kategoriTemuan: '',
  deskripsiTemuan: '',
  fotoSebelum: '',
  lokasi: '',
  tindakanPerbaikan: '',
  targetSelesai: '',
  status: 'Open',
  aktualClose: '',
  businessUnitId: null,
  plantId: null,
});

const form = ref(defaultForm());

function cancelForm() {
  showForm.value = false;
  editingId.value = null;
  form.value = defaultForm();
  clearPhotos();
}

function onBusinessUnitChange() {
  form.value.plantId = null;
}

// Alias for backward compat within this file
function showMessage(msg, type = 'success') {
  showToast(msg, type);
}

async function loadData(silent = false) {
  loading.value = true;
  try {
    records.value = await inspectionK3LService.list();
  } catch (e) {
    if (!silent) {
      showToast(e.message, 'error');
    }
  } finally {
    loading.value = false;
  }
}

async function loadLocationOptions(silent = false) {
  try {
    const [units, plantOptions] = await Promise.all([
      inspectionK3LService.listBusinessUnits(),
      inspectionK3LService.listPlants(),
    ]);
    businessUnits.value = units;
    plants.value = plantOptions;
  } catch (e) {
    if (!silent) {
      showToast(e.message, 'error');
    }
  }
}

async function submitForm() {
  submitting.value = true;
  try {
    // Upload new files to Cloudinary; keep existing URLs as-is
    let fotoSebelum = null;
    if (photos.value.length > 0) {
      const urls = [];
      for (const photo of photos.value) {
        if (photo.file) {
          urls.push(await uploadImage(photo.file));
        } else if (photo.preview) {
          // Already a Cloudinary URL from a previous save
          urls.push(photo.preview);
        }
      }
      fotoSebelum = JSON.stringify(urls);
    }

    const payload = {
      tanggal: form.value.tanggal,
      kategoriTemuan: form.value.kategoriTemuan,
      deskripsiTemuan: form.value.deskripsiTemuan || null,
      fotoSebelum: fotoSebelum,
      fotoSesudah: null,
      lokasi: form.value.lokasi || null,
      tindakanPerbaikan: form.value.tindakanPerbaikan || null,
      targetSelesai: form.value.targetSelesai || null,
      status: form.value.status || 'Open',
      aktualClose: form.value.aktualClose || null,
      businessUnitId: form.value.businessUnitId || null,
      plantId: form.value.plantId || null,
    };

    if (editingId.value) {
      await inspectionK3LService.update(editingId.value, payload);
      showMessage('Data berhasil diupdate');
    } else {
      await inspectionK3LService.create(payload);
      showMessage('Data berhasil disimpan');
    }
    cancelForm();
    await loadData();
  } catch (e) {
    showMessage(e.message, 'error');
  } finally {
    submitting.value = false;
  }
}


function editRecord(item) {
  editingId.value = item.id;
  form.value = {
    tanggal: item.tanggal,
    kategoriTemuan: item.kategoriTemuan,
    deskripsiTemuan: item.deskripsiTemuan || '',
    fotoSebelum: item.fotoSebelum || '',
    lokasi: item.lokasi || '',
    tindakanPerbaikan: item.tindakanPerbaikan || '',
    targetSelesai: item.targetSelesai || '',
    status: item.status,
    aktualClose: item.aktualClose || '',
    businessUnitId: item.businessUnitId || null,
    plantId: item.plantId || null,
  };
  // Load existing photos
  clearPhotos();
  if (item.fotoSebelum) {
    try {
      const parsed = JSON.parse(item.fotoSebelum);
      if (Array.isArray(parsed)) {
        photos.value = parsed.map((url) => ({ file: null, preview: url }));
      } else {
        photos.value = [{ file: null, preview: item.fotoSebelum }];
      }
    } catch {
      // Single URL string (legacy)
      photos.value = [{ file: null, preview: item.fotoSebelum }];
    }
  }
  showForm.value = true;
}

async function deleteRecord(id) {
  if (!confirm('Yakin ingin menghapus data ini?')) return;
  try {
    await inspectionK3LService.delete(id);
    showMessage('Data berhasil dihapus');
    await loadData();
  } catch (e) {
    showMessage(e.message, 'error');
  }
}

onMounted(() => {
  loadData(true);
  loadLocationOptions(true);
});
</script>

<style scoped>
.inspection-k3l {
  padding: 32px;
  max-width: 1200px;
}

.page-header {
  margin-bottom: 16px;
}

.page-header h2 {
  font-size: 22px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.subtitle {
  color: #64748b;
  font-size: 14px;
  margin-top: 4px;
}

/* Action bar */
.action-bar {
  margin-bottom: 16px;
}

/* Buttons */
.btn {
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition:
    background 0.15s,
    opacity 0.15s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #3b82f6;
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-secondary {
  background: #e2e8f0;
  color: #475569;
}

.btn-secondary:hover:not(:disabled) {
  background: #cbd5e1;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 13px;
  background: #f1f5f9;
  color: #475569;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
}

.btn-sm:hover:not(:disabled) {
  background: #e2e8f0;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  color: #64748b;
  transition:
    background 0.15s,
    color 0.15s;
}

.btn-icon:hover {
  background: #f1f5f9;
  color: #3b82f6;
}

.btn-danger:hover {
  background: #fef2f2;
  color: #ef4444;
}

/* Form card */
.form-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid #e2e8f0;
  margin-bottom: 20px;
}

.form-title {
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 20px 0;
}

.form-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-section {
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 16px;
}

.form-section:last-of-type {
  border-bottom: none;
  padding-bottom: 0;
}

.section-title {
  font-size: 13px;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 12px 0;
}

.form-row {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 200px;
  max-width: 300px;
  flex: 1;
}

.form-group.full-width {
  flex-basis: 100%;
  max-width: 100%;
}

.form-row-fill {
  flex-wrap: nowrap;
}

.form-group-fill {
  max-width: none;
  flex: 1;
}

.form-group label {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
}

.required {
  color: #ef4444;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  color: #1e293b;
  background: #fff;
  transition: border-color 0.15s;
}

.form-group select {
  cursor: pointer;
}

.form-group select:disabled {
  cursor: not-allowed;
  background: #f1f5f9;
  color: #94a3b8;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-group textarea {
  resize: vertical;
}

/* Date input with calendar icon */
.date-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.date-input-wrapper input {
  width: 100%;
  padding-right: 36px;
}

.date-icon {
  position: absolute;
  right: 10px;
  color: #94a3b8;
  cursor: pointer;
  transition: color 0.15s;
}

.date-icon:hover {
  color: #3b82f6;
}

/* Photo upload */
.photo-count {
  font-weight: 400;
  color: #94a3b8;
  font-size: 12px;
}

.photo-upload {
  border: 2px dashed #e2e8f0;
  border-radius: 8px;
  padding: 16px;
}

.photo-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 12px;
}

.photo-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.photo-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 12px 20px;
  border-radius: 8px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  color: #475569;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition:
    background 0.15s,
    border-color 0.15s;
}

.photo-btn:hover {
  background: #f1f5f9;
  border-color: #3b82f6;
  color: #3b82f6;
}

.photo-preview {
  position: relative;
  display: inline-block;
}

.photo-preview img {
  width: 100px;
  height: 100px;
  border-radius: 8px;
  object-fit: cover;
  border: 1px solid #e2e8f0;
}

.photo-remove {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #ef4444;
  color: #fff;
  border: none;
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.photo-clear {
  margin-top: 8px;
  text-align: left;
}

.btn-clear {
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 600;
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-clear:hover {
  background: #fee2e2;
}

.form-actions {
  display: flex;
  gap: 12px;
  padding-top: 8px;
}

/* Toast notification */
.toast {
  position: fixed;
  top: 24px;
  right: 24px;
  z-index: 9999;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  max-width: 400px;
}

.toast-success {
  background: #f0fdf4;
  color: #166534;
  border: 1px solid #bbf7d0;
}

.toast-error {
  background: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.toast-warning {
  background: #fffbeb;
  color: #92400e;
  border: 1px solid #fde68a;
}

.toast-text {
  flex: 1;
}

.toast-close {
  background: none;
  border: none;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  color: inherit;
  opacity: 0.6;
  padding: 0 4px;
}

.toast-close:hover {
  opacity: 1;
}

/* Toast transition */
.toast-enter-active {
  transition: all 0.3s ease;
}

.toast-leave-active {
  transition: all 0.25s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(40px);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(40px);
}

/* Table */
.table-card {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  overflow: hidden;
}

.table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #f1f5f9;
}

.table-header h3 {
  font-size: 15px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.table-wrapper {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: #f8fafc;
}

th {
  padding: 10px 14px;
  text-align: left;
  font-size: 12px;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

td {
  padding: 12px 14px;
  font-size: 14px;
  color: #334155;
  border-top: 1px solid #f1f5f9;
}

.td-desc {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.td-actions {
  display: flex;
  gap: 4px;
  white-space: nowrap;
}

tbody tr:hover {
  background: #f8fafc;
}

/* Status badges */
.status-badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.status-open {
  background: #fef3c7;
  color: #92400e;
}

.status-in-progress {
  background: #dbeafe;
  color: #1e40af;
}

.status-closed {
  background: #dcfce7;
  color: #166534;
}

/* Empty state */
.empty-state {
  padding: 40px 20px;
  text-align: center;
  color: #94a3b8;
  font-size: 14px;
}
</style>
