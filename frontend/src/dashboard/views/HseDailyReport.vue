<template>
  <div class="page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">HSE Daily Report</h1>
        <p class="page-sub">Laporan harian aktivitas keselamatan kerja</p>
      </div>
      <button class="btn-primary" @click="openCreate">+ Tambah Laporan</button>
    </div>

    <!-- Empty state -->
    <div v-if="!loading && records.length === 0" class="empty-state">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5.586a1 1 0 0 1 .707.293l5.414 5.414a1 1 0 0 1 .293.707V19a2 2 0 0 1-2 2z"/>
      </svg>
      <p>Belum ada laporan</p>
      <button class="btn-primary" @click="openCreate">+ Tambah Laporan Pertama</button>
    </div>

    <!-- Table -->
    <div v-else class="table-card">
      <!-- Date filter row -->
      <div class="date-filter-row">
        <button v-for="opt in DATE_PRESETS" :key="opt.value" class="date-chip" :class="{ active: filterDate === opt.value }" @click="setDatePreset(opt.value)">{{ opt.label }}</button>
        <template v-if="filterDate === 'custom'">
          <label class="toolbar-date-wrap">
            <input type="date" v-model="customDateFrom" class="toolbar-date" @click="$event.target.showPicker?.()" />
          </label>
          <span class="date-sep">–</span>
          <label class="toolbar-date-wrap">
            <input type="date" v-model="customDateTo" class="toolbar-date" @click="$event.target.showPicker?.()" />
          </label>
        </template>
      </div>
      <!-- Toolbar -->
      <div class="table-toolbar">
        <div class="search-box">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input v-model="search" type="text" placeholder="Cari pekerjaan, lokasi, pekerja…" />
          <button v-if="search" class="search-clear" @click="search = ''">✕</button>
        </div>
        <select v-model="filterJenis" class="toolbar-select">
          <option value="">Semua Jenis</option>
          <option v-for="opt in JENIS_OPTIONS" :key="opt" :value="opt">{{ opt }}</option>
        </select>
        <select v-model="filterRisiko" class="toolbar-select">
          <option value="">Semua Risiko</option>
          <option value="Rendah">Rendah</option>
          <option value="Sedang">Sedang</option>
          <option value="Tinggi">Tinggi</option>
        </select>
        <button v-if="hasActiveFilter" class="btn-reset-filter" @click="resetFilters">Reset</button>
      </div>

      <div v-if="loading" class="loading">Memuat data…</div>
      <div v-else class="table-scroll">
      <table>
        <thead>
          <tr>
            <th>Tanggal</th>
            <th>Pekerjaan</th>
            <th>Lokasi</th>
            <th>Jenis Pekerjaan</th>
            <th>Level Risiko</th>
            <th>Pengawas HSE</th>
            <th>Permit</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in filteredRecords" :key="r.id" @click="openView(r)" class="row-clickable">
            <td>{{ formatDate(r.tanggal) }}</td>
            <td class="col-pekerjaan">{{ firstBullet(r.pekerjaan) }}</td>
            <td>{{ r.lokasiPekerjaan || '-' }}</td>
            <td>{{ displayJenis(r) }}</td>
            <td><span class="badge-risiko" :class="r.levelRisiko?.toLowerCase()">{{ r.levelRisiko || '-' }}</span></td>
            <td>{{ r.pengawasHse || '-' }}</td>
            <td><span class="badge-permit" :class="r.statusPermit ? 'ada' : 'tidak'">{{ r.statusPermit ? 'Ada' : 'Tidak' }}</span></td>
            <td class="col-actions" @click.stop>
              <button class="btn-icon" @click="openEdit(r)" title="Edit">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
              </button>
              <button class="btn-icon danger" @click="confirmDelete(r)" title="Hapus">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/></svg>
              </button>
            </td>
          </tr>
          <tr v-if="filteredRecords.length === 0">
            <td colspan="8" class="no-results">Tidak ada data yang cocok</td>
          </tr>
        </tbody>
      </table>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="modal.open" class="modal-overlay" @mousedown.self="tryClose">
      <div class="modal">
        <div class="modal-header">
          <h2>{{ modal.mode === 'view' ? 'Detail Laporan' : modal.mode === 'edit' ? 'Edit Laporan' : 'Tambah Laporan' }}</h2>
          <button class="btn-close" @click="tryClose">✕</button>
        </div>

        <!-- View mode -->
        <div v-if="modal.mode === 'view'" class="view-body">
          <!-- Banner: first photo -->
          <div v-if="parseFotos(modal.record.foto).length" class="view-banner" @click="openLightbox(parseFotos(modal.record.foto), 0)">
            <img :src="parseFotos(modal.record.foto)[0]" />
            <span v-if="parseFotos(modal.record.foto).length > 1" class="view-banner-count">+{{ parseFotos(modal.record.foto).length - 1 }} foto</span>
          </div>

          <div class="view-scroll">
            <!-- 3-column meta grid -->
            <div class="view-meta-grid">
              <div class="view-meta-item">
                <span class="view-label">Hari/Tanggal</span>
                <span class="view-val">{{ formatDateFull(modal.record.tanggal) }}</span>
              </div>
              <div class="view-meta-item">
                <span class="view-label">Lokasi</span>
                <span class="view-val">{{ modal.record.lokasiPekerjaan || '-' }}</span>
              </div>
              <div class="view-meta-item">
                <span class="view-label">Pekerja</span>
                <span class="view-val">{{ modal.record.pekerja || '-' }}</span>
              </div>
              <div class="view-meta-item">
                <span class="view-label">Department</span>
                <span class="view-val">{{ modal.record.departmentName || '-' }}</span>
              </div>
              <div class="view-meta-item">
                <span class="view-label">Business Unit</span>
                <span class="view-val">{{ modal.record.businessUnitName || '-' }}</span>
              </div>
              <div class="view-meta-item">
                <span class="view-label">Plant</span>
                <span class="view-val">{{ modal.record.plantName || '-' }}</span>
              </div>
              <div class="view-meta-item">
                <span class="view-label">Status Permit</span>
                <span class="view-val"><span class="badge-permit" :class="modal.record.statusPermit ? 'ada' : 'tidak'">{{ modal.record.statusPermit ? 'Ada' : 'Tidak Ada' }}</span></span>
              </div>
              <div v-if="modal.record.statusPermit" class="view-meta-item">
                <span class="view-label">No. Permit</span>
                <span class="view-val">{{ modal.record.noPermit || '-' }}</span>
              </div>
              <div class="view-meta-item">
                <span class="view-label">Jenis Pekerjaan</span>
                <span class="view-val">{{ displayJenis(modal.record) }}</span>
              </div>
              <div class="view-meta-item">
                <span class="view-label">Level Risiko</span>
                <span class="view-val"><span class="badge-risiko" :class="modal.record.levelRisiko?.toLowerCase()">{{ modal.record.levelRisiko || '-' }}</span></span>
              </div>
              <div class="view-meta-item">
                <span class="view-label">Pengawas HSE</span>
                <span class="view-val">{{ modal.record.pengawasHse || '-' }}</span>
              </div>
            </div>

            <!-- 2-column detail sections -->
            <div class="view-detail-cols">
              <div class="view-detail-col">
                <div class="view-section">
                  <div class="view-section-label">Pekerjaan</div>
                  <ul class="view-bullets"><li v-for="(item, i) in parseBullets(modal.record.pekerjaan)" :key="i">{{ item }}</li></ul>
                </div>
                <div v-if="parseBullets(modal.record.potensiBahaya).length" class="view-section">
                  <div class="view-section-label">Potensi Bahaya</div>
                  <ol class="view-bullets"><li v-for="(item, i) in parseBullets(modal.record.potensiBahaya)" :key="i">{{ item }}</li></ol>
                </div>
              </div>
              <div class="view-detail-col">
                <div v-if="parseBullets(modal.record.pengendalianBahaya).length" class="view-section">
                  <div class="view-section-label">Pengendalian Bahaya</div>
                  <ul class="view-bullets"><li v-for="(item, i) in parseBullets(modal.record.pengendalianBahaya)" :key="i">{{ item }}</li></ul>
                </div>
                <div v-if="parseBullets(modal.record.saranMasukan).length" class="view-section">
                  <div class="view-section-label">Saran / Masukan</div>
                  <ul class="view-bullets"><li v-for="(item, i) in parseBullets(modal.record.saranMasukan)" :key="i">{{ item }}</li></ul>
                </div>
              </div>
            </div>

            <!-- Extra photos -->
            <div v-if="parseFotos(modal.record.foto).length > 1" class="view-section">
              <div class="view-section-label">Dokumentasi Lainnya</div>
              <div class="foto-grid">
                <img v-for="(url, i) in parseFotos(modal.record.foto).slice(1)" :key="i" :src="url" class="foto-thumb" @click="openLightbox(parseFotos(modal.record.foto), i + 1)" />
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn-secondary" @click="modal.open = false">Tutup</button>
            <button class="btn-primary" @click="openEdit(modal.record)">Edit</button>
          </div>
        </div>

        <!-- Create / Edit form -->
        <form v-else @submit.prevent="submitForm" class="modal-form">
          <div class="form-scroll">
            <!-- Section: Identitas -->
            <div class="form-section-title">Identitas Pekerjaan</div>
            <div class="form-row">
              <div class="form-group">
                <label>Tanggal <span class="req">*</span></label>
                <input type="date" v-model="form.tanggal" required />
              </div>
              <div class="form-group">
                <label>Lokasi Pekerjaan</label>
                <input type="text" v-model="form.lokasiPekerjaan" placeholder="Contoh: Silo Dryer" />
              </div>
            </div>

            <!-- Pekerjaan bullets -->
            <div class="form-group">
              <label>Pekerjaan <span class="req">*</span></label>
              <div class="bullet-list">
                <div v-for="(item, i) in form.pekerjaan" :key="i" class="bullet-row">
                  <span class="bullet-dot">•</span>
                  <input type="text" v-model="form.pekerjaan[i]" placeholder="Deskripsi pekerjaan" @keydown.enter.prevent="addBullet('pekerjaan', i)" />
                  <button type="button" class="btn-remove-bullet" @click="removeBullet('pekerjaan', i)" :disabled="form.pekerjaan.length === 1">✕</button>
                </div>
                <button type="button" class="btn-add-bullet" @click="addBullet('pekerjaan')">+ Tambah pekerjaan</button>
              </div>
            </div>

            <!-- Pekerja -->
            <div class="form-group">
              <label>Pekerja <span class="req">*</span></label>
              <input type="text" v-model="form.pekerja" placeholder="Nama pekerja (pisah koma jika lebih dari satu)" required />
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Department</label>
                <select v-model.number="form.departmentId">
                  <option :value="null">Pilih Department</option>
                  <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option>
                </select>
              </div>
              <div class="form-group">
                <label>Business Unit <span class="field-auto-tag">Otomatis</span></label>
                <input type="text" :value="currentUser?.businessUnit || '-'" disabled class="field-auto" />
              </div>
              <div class="form-group">
                <label>Plant <span class="field-auto-tag">Otomatis</span></label>
                <input type="text" :value="currentUser?.plant || '-'" disabled class="field-auto" />
              </div>
            </div>

            <!-- Section: Permit -->
            <div class="form-section-title">Informasi Permit</div>
            <div class="form-row">
              <div class="form-group">
                <label>Status Permit</label>
                <div class="toggle-row">
                  <label class="toggle">
                    <input type="checkbox" v-model="form.statusPermit" />
                    <span class="toggle-slider"></span>
                  </label>
                  <span class="toggle-label">{{ form.statusPermit ? 'Ada' : 'Tidak Ada' }}</span>
                </div>
              </div>
              <div class="form-group" v-if="form.statusPermit">
                <label>No. Permit</label>
                <input type="text" v-model="form.noPermit" placeholder="Nomor permit" />
              </div>
            </div>

            <!-- Section: Jenis Pekerjaan -->
            <div class="form-section-title">Analisis Risiko</div>
            <div class="form-row">
              <div class="form-group">
                <label>Jenis Pekerjaan</label>
                <select v-model="form.jenisPekerjaan">
                  <option value="">Pilih jenis pekerjaan</option>
                  <option v-for="opt in JENIS_OPTIONS" :key="opt" :value="opt">{{ opt }}</option>
                </select>
              </div>
              <div class="form-group" v-if="form.jenisPekerjaan === 'Lainnya'">
                <label>Jenis Pekerjaan Lainnya</label>
                <input type="text" v-model="form.jenisPekerjaanLainnya" placeholder="Sebutkan jenis pekerjaan" />
              </div>
              <div class="form-group">
                <label>Level Risiko</label>
                <select v-model="form.levelRisiko">
                  <option value="">Pilih level risiko</option>
                  <option value="Rendah">Rendah</option>
                  <option value="Sedang">Sedang</option>
                  <option value="Tinggi">Tinggi</option>
                </select>
              </div>
            </div>

            <!-- Potensi Bahaya bullets -->
            <div class="form-group">
              <label>Potensi Bahaya</label>
              <div class="bullet-list">
                <div v-for="(item, i) in form.potensiBahaya" :key="i" class="bullet-row numbered">
                  <span class="bullet-dot">{{ i + 1 }}.</span>
                  <input type="text" v-model="form.potensiBahaya[i]" placeholder="Potensi bahaya" @keydown.enter.prevent="addBullet('potensiBahaya', i)" />
                  <button type="button" class="btn-remove-bullet" @click="removeBullet('potensiBahaya', i)" :disabled="form.potensiBahaya.length === 1">✕</button>
                </div>
                <button type="button" class="btn-add-bullet" @click="addBullet('potensiBahaya')">+ Tambah bahaya</button>
              </div>
            </div>

            <!-- Pengendalian Bahaya bullets -->
            <div class="form-group">
              <label>Pengendalian Bahaya</label>
              <div class="bullet-list">
                <div v-for="(item, i) in form.pengendalianBahaya" :key="i" class="bullet-row">
                  <span class="bullet-dot">•</span>
                  <input type="text" v-model="form.pengendalianBahaya[i]" placeholder="Tindakan pengendalian" @keydown.enter.prevent="addBullet('pengendalianBahaya', i)" />
                  <button type="button" class="btn-remove-bullet" @click="removeBullet('pengendalianBahaya', i)" :disabled="form.pengendalianBahaya.length === 1">✕</button>
                </div>
                <button type="button" class="btn-add-bullet" @click="addBullet('pengendalianBahaya')">+ Tambah pengendalian</button>
              </div>
            </div>

            <!-- Section: HSE & Notes -->
            <div class="form-section-title">Pengawasan & Catatan</div>
            <div class="form-group">
              <label>Pengawas HSE</label>
              <input type="text" v-model="form.pengawasHse" placeholder="Nama pengawas HSE" />
            </div>

            <!-- Saran bullets -->
            <div class="form-group">
              <label>Saran / Masukan</label>
              <div class="bullet-list">
                <div v-for="(item, i) in form.saranMasukan" :key="i" class="bullet-row">
                  <span class="bullet-dot">•</span>
                  <input type="text" v-model="form.saranMasukan[i]" placeholder="Saran atau masukan" @keydown.enter.prevent="addBullet('saranMasukan', i)" />
                  <button type="button" class="btn-remove-bullet" @click="removeBullet('saranMasukan', i)" :disabled="form.saranMasukan.length === 1">✕</button>
                </div>
                <button type="button" class="btn-add-bullet" @click="addBullet('saranMasukan')">+ Tambah saran</button>
              </div>
            </div>

            <!-- Section: Foto -->
            <div class="form-section-title">Dokumentasi</div>
            <div class="form-group">
              <div class="foto-label-row">
                <label>Foto <span class="photo-count-label">({{ form.fotos.length }}/10)</span></label>
                <button v-if="form.fotos.length > 0" type="button" class="btn-clear-fotos" @click="clearFotos">Hapus Semua</button>
              </div>
              <div class="foto-upload-area">
                <div class="foto-preview-grid">
                  <div v-for="(photo, i) in form.fotos" :key="i" class="foto-preview-item">
                    <img :src="photo.preview" />
                    <button type="button" class="btn-remove-foto" @click="removeFoto(i)">✕</button>
                  </div>
                  <label v-if="form.fotos.length < 10" class="foto-add-btn">
                    <input type="file" accept="image/*" multiple @change="onFotoSelect" style="display:none" />
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
                    <span>Tambah foto</span>
                  </label>
                </div>
              </div>
            </div>
          </div>

          <div v-if="photoWarning" class="form-warning">{{ photoWarning }}</div>
          <div v-if="formError" class="form-error">{{ formError }}</div>

          <div class="modal-footer">
            <button type="button" class="btn-secondary" @click="tryClose">Batal</button>
            <button type="submit" class="btn-primary" :disabled="submitting">
              {{ submitting ? 'Menyimpan…' : modal.mode === 'edit' ? 'Simpan Perubahan' : 'Simpan' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Lightbox -->
    <div v-if="lightbox" class="lightbox" @click.self="lightbox = null" @keydown.left="lbPrev" @keydown.right="lbNext" @keydown.esc="lightbox = null" tabindex="0">
      <button class="lb-close" @click="lightbox = null">✕</button>
      <button v-if="lightbox.urls.length > 1" class="lb-nav lb-prev" @click.stop="lbPrev">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
      </button>
      <img :src="lightbox.urls[lightbox.index]" />
      <button v-if="lightbox.urls.length > 1" class="lb-nav lb-next" @click.stop="lbNext">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
      </button>
      <div v-if="lightbox.urls.length > 1" class="lb-dots">
        <span v-for="(_, i) in lightbox.urls" :key="i" class="lb-dot" :class="{ active: i === lightbox.index }" @click.stop="lightbox.index = i"></span>
      </div>
    </div>

    <!-- Delete confirm -->
    <div v-if="deleteTarget" class="modal-overlay" @mousedown.self="deleteTarget = null">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h2>Hapus Laporan?</h2>
          <button class="btn-close" @click="deleteTarget = null">✕</button>
        </div>
        <p class="delete-msg">Laporan tanggal <strong>{{ formatDate(deleteTarget.tanggal) }}</strong> akan dihapus permanen.</p>
        <div class="modal-footer">
          <button class="btn-secondary" @click="deleteTarget = null">Batal</button>
          <button class="btn-danger" @click="doDelete" :disabled="submitting">{{ submitting ? 'Menghapus…' : 'Hapus' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue';
import { authService } from '@/services/authService.js';
import { hseDailyService, uploadImage } from '@/services/hseDailyService.js';

const JENIS_OPTIONS = [
  'Ketinggian',
  'Pekerjaan Listrik',
  'Ruang Terbatas',
  'Pekerjaan Panas (Hot Work)',
  'Bahan Kimia',
  'Penggalian',
  'Lainnya',
];

const currentUser = authService.getCurrentUser();
const records = ref([]);
const departments = ref([]);
const loading = ref(true);
const submitting = ref(false);
const formError = ref('');
const photoWarning = ref('');
const lightbox = ref(null); // { urls: string[], index: number }
const deleteTarget = ref(null);

const search = ref('');
const filterJenis = ref('');
const filterRisiko = ref('');
const filterDate = ref('all');
const customDateFrom = ref('');
const customDateTo = ref('');

const DATE_PRESETS = [
  { label: 'Semua', value: 'all' },
  { label: 'Hari ini', value: 'today' },
  { label: 'Minggu ini', value: 'week' },
  { label: 'Bulan ini', value: 'month' },
  { label: 'Kustom', value: 'custom' },
];

function setDatePreset(val) {
  filterDate.value = val;
  if (val !== 'custom') { customDateFrom.value = ''; customDateTo.value = ''; }
}

function resetFilters() {
  search.value = '';
  filterJenis.value = '';
  filterRisiko.value = '';
  filterDate.value = 'all';
  customDateFrom.value = '';
  customDateTo.value = '';
}

const hasActiveFilter = computed(() =>
  search.value || filterJenis.value || filterRisiko.value || filterDate.value !== 'all'
);

const filteredRecords = computed(() => {
  const q = search.value.trim().toLowerCase();
  const today = new Date(); today.setHours(0, 0, 0, 0);

  return records.value.filter(r => {
    if (filterJenis.value && r.jenisPekerjaan !== filterJenis.value) return false;
    if (filterRisiko.value && r.levelRisiko !== filterRisiko.value) return false;
    if (q) {
      const hay = [r.pekerjaan, r.lokasiPekerjaan, r.pekerja, r.pengawasHse, r.jenisPekerjaanLainnya]
        .filter(Boolean).join(' ').toLowerCase();
      if (!hay.includes(q)) return false;
    }
    if (filterDate.value !== 'all') {
      const d = new Date(r.tanggal); d.setHours(0, 0, 0, 0);
      if (filterDate.value === 'today') {
        if (d.getTime() !== today.getTime()) return false;
      } else if (filterDate.value === 'week') {
        const start = new Date(today); start.setDate(today.getDate() - today.getDay());
        const end = new Date(start); end.setDate(start.getDate() + 6);
        if (d < start || d > end) return false;
      } else if (filterDate.value === 'month') {
        if (d.getMonth() !== today.getMonth() || d.getFullYear() !== today.getFullYear()) return false;
      } else if (filterDate.value === 'custom') {
        if (customDateFrom.value) { const from = new Date(customDateFrom.value); from.setHours(0,0,0,0); if (d < from) return false; }
        if (customDateTo.value)   { const to   = new Date(customDateTo.value);   to.setHours(0,0,0,0);   if (d > to)   return false; }
      }
    }
    return true;
  });
});

let photoWarnTimer = null;
function showPhotoWarning(msg) {
  photoWarning.value = msg;
  if (photoWarnTimer) clearTimeout(photoWarnTimer);
  photoWarnTimer = setTimeout(() => { photoWarning.value = ''; }, 3500);
}

const modal = ref({ open: false, mode: 'create', record: null });

const defaultForm = () => ({
  tanggal: new Date().toISOString().slice(0, 10),
  pekerjaan: [''],
  pekerja: '',
  departmentId: null,
  lokasiPekerjaan: '',
  statusPermit: false,
  noPermit: '',
  jenisPekerjaan: '',
  jenisPekerjaanLainnya: '',
  potensiBahaya: [''],
  levelRisiko: '',
  pengendalianBahaya: [''],
  pengawasHse: '',
  saranMasukan: [''],
  fotos: [], // [{ file: File|null, preview: string }]
  businessUnitId: currentUser?.businessUnitId ?? null,
  plantId: currentUser?.plantId ?? null,
});

const form = ref(defaultForm());

onMounted(async () => {
  try {
    [records.value, departments.value] = await Promise.all([
      hseDailyService.list(),
      hseDailyService.listDepartments(),
    ]);
  } finally {
    loading.value = false;
  }
});

// ── Bullet helpers ─────────────────────────────────────────────────────
function addBullet(field, afterIndex = null) {
  if (afterIndex !== null) {
    form.value[field].splice(afterIndex + 1, 0, '');
  } else {
    form.value[field].push('');
  }
}

function removeBullet(field, index) {
  if (form.value[field].length > 1) {
    form.value[field].splice(index, 1);
  }
}

function bulletsToJson(arr) {
  const clean = arr.map(s => s.trim()).filter(Boolean);
  return clean.length ? JSON.stringify(clean) : null;
}

function parseBullets(raw) {
  if (!raw) return [];
  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [raw];
  } catch {
    return raw.split('\n').filter(Boolean);
  }
}

function firstBullet(raw) {
  const items = parseBullets(raw);
  if (!items.length) return '-';
  return items.length > 1 ? `${items[0]} +${items.length - 1} lainnya` : items[0];
}

// ── Photo helpers ──────────────────────────────────────────────────────
function parseFotos(raw) {
  if (!raw) return [];
  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [raw];
  } catch {
    return [raw];
  }
}

function onFotoSelect(e) {
  const files = Array.from(e.target.files);
  e.target.value = '';
  if (!files.length) return;
  const remaining = 10 - form.value.fotos.length;
  if (files.length > remaining) {
    showPhotoWarning(
      remaining > 0
        ? `Maksimal 10 foto. Hanya dapat menambahkan ${remaining} foto lagi.`
        : 'Batas 10 foto sudah tercapai.'
    );
    return;
  }
  for (const file of files) {
    form.value.fotos.push({ file, preview: URL.createObjectURL(file) });
  }
}

function removeFoto(index) {
  const photo = form.value.fotos[index];
  if (photo.preview?.startsWith('blob:')) URL.revokeObjectURL(photo.preview);
  form.value.fotos.splice(index, 1);
}

function clearFotos() {
  form.value.fotos.forEach(p => { if (p.preview?.startsWith('blob:')) URL.revokeObjectURL(p.preview); });
  form.value.fotos = [];
}

async function uploadFotoList() {
  if (!form.value.fotos.length) return null;
  const urls = [];
  for (const photo of form.value.fotos) {
    if (photo.file) {
      urls.push(await uploadImage(photo.file));
    } else if (photo.preview) {
      urls.push(photo.preview);
    }
  }
  return JSON.stringify(urls);
}

function openLightbox(urls, index = 0) {
  const list = Array.isArray(urls) ? urls : [urls];
  lightbox.value = { urls: list, index };
  nextTick(() => document.querySelector('.lightbox')?.focus());
}
function lbPrev() {
  if (!lightbox.value) return;
  lightbox.value.index = (lightbox.value.index - 1 + lightbox.value.urls.length) % lightbox.value.urls.length;
}
function lbNext() {
  if (!lightbox.value) return;
  lightbox.value.index = (lightbox.value.index + 1) % lightbox.value.urls.length;
}

// ── Modal ──────────────────────────────────────────────────────────────
function openCreate() {
  clearFotos();
  form.value = defaultForm();
  formError.value = '';
  photoWarning.value = '';
  modal.value = { open: true, mode: 'create', record: null };
}

function openEdit(record) {
  clearFotos();
  formError.value = '';
  photoWarning.value = '';
  form.value = {
    tanggal: record.tanggal?.slice(0, 10) || '',
    pekerjaan: parseBullets(record.pekerjaan).length ? parseBullets(record.pekerjaan) : [''],
    pekerja: record.pekerja || '',
    departmentId: record.departmentId ?? null,
    lokasiPekerjaan: record.lokasiPekerjaan || '',
    statusPermit: record.statusPermit || false,
    noPermit: record.noPermit || '',
    jenisPekerjaan: record.jenisPekerjaan || '',
    jenisPekerjaanLainnya: record.jenisPekerjaanLainnya || '',
    potensiBahaya: parseBullets(record.potensiBahaya).length ? parseBullets(record.potensiBahaya) : [''],
    levelRisiko: record.levelRisiko || '',
    pengendalianBahaya: parseBullets(record.pengendalianBahaya).length ? parseBullets(record.pengendalianBahaya) : [''],
    pengawasHse: record.pengawasHse || '',
    saranMasukan: parseBullets(record.saranMasukan).length ? parseBullets(record.saranMasukan) : [''],
    fotos: parseFotos(record.foto).map(url => ({ file: null, preview: url })),
    businessUnitId: record.businessUnitId ?? currentUser?.businessUnitId ?? null,
    plantId: record.plantId ?? currentUser?.plantId ?? null,
  };
  formError.value = '';
  modal.value = { open: true, mode: 'edit', record };
}

function openView(record) {
  modal.value = { open: true, mode: 'view', record };
}

function tryClose() {
  modal.value.open = false;
}

// ── Display helpers ────────────────────────────────────────────────────
function displayJenis(r) {
  if (!r.jenisPekerjaan) return '-';
  if (r.jenisPekerjaan === 'Lainnya') return r.jenisPekerjaanLainnya || 'Lainnya';
  return r.jenisPekerjaan;
}

function formatDate(d) {
  if (!d) return '-';
  return new Date(d).toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' });
}

function formatDateFull(d) {
  if (!d) return '-';
  return new Date(d).toLocaleDateString('id-ID', { weekday: 'long', day: '2-digit', month: 'long', year: 'numeric' });
}

// ── Submit ─────────────────────────────────────────────────────────────
async function submitForm() {
  formError.value = '';
  const clean = form.value.pekerjaan.map(s => s.trim()).filter(Boolean);
  if (!clean.length) { formError.value = 'Pekerjaan wajib diisi'; return; }
  if (!form.value.pekerja.trim()) { formError.value = 'Pekerja wajib diisi'; return; }

  submitting.value = true;
  try {
    const payload = {
      tanggal: form.value.tanggal,
      pekerjaan: bulletsToJson(form.value.pekerjaan),
      pekerja: form.value.pekerja.trim(),
      lokasiPekerjaan: form.value.lokasiPekerjaan || null,
      statusPermit: form.value.statusPermit,
      noPermit: form.value.statusPermit ? (form.value.noPermit || null) : null,
      jenisPekerjaan: form.value.jenisPekerjaan || null,
      jenisPekerjaanLainnya: form.value.jenisPekerjaan === 'Lainnya' ? (form.value.jenisPekerjaanLainnya || null) : null,
      potensiBahaya: bulletsToJson(form.value.potensiBahaya),
      levelRisiko: form.value.levelRisiko || null,
      pengendalianBahaya: bulletsToJson(form.value.pengendalianBahaya),
      pengawasHse: form.value.pengawasHse || null,
      saranMasukan: bulletsToJson(form.value.saranMasukan),
      foto: await uploadFotoList(),
      departmentId: form.value.departmentId,
      businessUnitId: form.value.businessUnitId,
      plantId: form.value.plantId,
    };

    if (modal.value.mode === 'edit') {
      await hseDailyService.update(modal.value.record.id, payload);
    } else {
      await hseDailyService.create(payload);
    }

    records.value = await hseDailyService.list();
    modal.value.open = false;
  } catch (err) {
    formError.value = err.message;
  } finally {
    submitting.value = false;
  }
}

// ── Delete ─────────────────────────────────────────────────────────────
function confirmDelete(r) {
  deleteTarget.value = r;
}

async function doDelete() {
  submitting.value = true;
  try {
    await hseDailyService.delete(deleteTarget.value.id);
    records.value = records.value.filter(r => r.id !== deleteTarget.value.id);
    deleteTarget.value = null;
  } catch (err) {
    formError.value = err.message;
  } finally {
    submitting.value = false;
  }
}
</script>

<style scoped>
.page { padding: 28px 32px; display: flex; flex-direction: column; gap: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; }
.page-title { font-size: 22px; font-weight: 700; color: #1e293b; margin: 0 0 4px; }
.page-sub { font-size: 13px; color: #94a3b8; margin: 0; }

.btn-primary { background: #3b82f6; color: #fff; border: none; border-radius: 8px; padding: 9px 18px; font-size: 14px; font-weight: 600; cursor: pointer; transition: background 0.15s; }
.btn-primary:hover { background: #2563eb; }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-secondary { background: #f1f5f9; color: #475569; border: 1px solid #e2e8f0; border-radius: 8px; padding: 9px 18px; font-size: 14px; font-weight: 500; cursor: pointer; }
.btn-secondary:hover { background: #e2e8f0; }
.btn-danger { background: #ef4444; color: #fff; border: none; border-radius: 8px; padding: 9px 18px; font-size: 14px; font-weight: 600; cursor: pointer; }
.btn-danger:hover { background: #dc2626; }
.btn-danger:disabled { opacity: 0.6; }

.empty-state { display: flex; flex-direction: column; align-items: center; gap: 16px; padding: 80px 20px; color: #94a3b8; }
.empty-state svg { width: 56px; height: 56px; }
.empty-state p { font-size: 15px; margin: 0; }

.table-card { background: #fff; border-radius: 12px; border: 1px solid #e5e7eb; overflow: hidden; }
.table-card table { min-width: 800px; }
.table-scroll { overflow-x: auto; -webkit-overflow-scrolling: touch; }
.loading { padding: 40px; text-align: center; color: #94a3b8; }
.table-toolbar { display: flex; align-items: center; gap: 10px; padding: 14px 16px; border-bottom: 1px solid #f1f5f9; flex-wrap: wrap; }
.search-box { display: flex; align-items: center; gap: 8px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0 10px; flex: 1; min-width: 200px; }
.search-box svg { width: 16px; height: 16px; color: #94a3b8; flex-shrink: 0; }
.search-box input { border: none; background: transparent; font-size: 13px; color: #1e293b; outline: none; flex: 1; padding: 8px 0; }
.search-box input::placeholder { color: #94a3b8; }
.search-clear { background: none; border: none; color: #94a3b8; cursor: pointer; font-size: 13px; padding: 0; line-height: 1; }
.search-clear:hover { color: #64748b; }
.toolbar-select { border: 1px solid #e2e8f0; border-radius: 8px; background: #f8fafc; color: #374151; font-size: 13px; padding: 8px 10px; outline: none; cursor: pointer; }
.toolbar-select:focus { border-color: #3b82f6; }
.btn-reset-filter { background: none; border: 1px solid #fca5a5; color: #ef4444; border-radius: 8px; font-size: 12px; padding: 7px 12px; cursor: pointer; white-space: nowrap; }
.btn-reset-filter:hover { background: #fee2e2; }
.date-filter-row { display: flex; align-items: center; gap: 6px; padding: 10px 16px; border-bottom: 1px solid #f1f5f9; flex-wrap: wrap; }
.date-chip { background: #f1f5f9; border: 1px solid transparent; border-radius: 20px; padding: 5px 14px; font-size: 13px; color: #64748b; cursor: pointer; transition: all 0.15s; white-space: nowrap; }
.date-chip:hover { background: #e2e8f0; color: #1e293b; }
.date-chip.active { background: #3b82f6; color: #fff; border-color: #3b82f6; }
.toolbar-date-wrap { display: inline-flex; border: 1px solid #cbd5e1; border-radius: 8px; background: #fff; overflow: hidden; cursor: pointer; transition: border-color 0.15s; }
.toolbar-date-wrap:focus-within { border-color: #3b82f6; }
.toolbar-date { border: none; background: transparent; color: #1e293b; font-size: 13px; padding: 6px 10px; outline: none; cursor: pointer; color-scheme: light; width: 140px; }
.date-sep { color: #94a3b8; font-size: 13px; }
.no-results { text-align: center; padding: 32px; color: #94a3b8; font-size: 14px; }
table { width: 100%; border-collapse: collapse; }
thead { background: #f8fafc; }
th { padding: 12px 16px; text-align: left; font-size: 12px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.04em; border-bottom: 1px solid #e5e7eb; white-space: nowrap; }
td { padding: 13px 16px; font-size: 14px; color: #374151; border-bottom: 1px solid #f1f5f9; }
.row-clickable { cursor: pointer; transition: background 0.1s; }
.row-clickable:hover { background: #f8fafc; }
.col-pekerjaan { max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.badge-risiko { display: inline-block; padding: 3px 8px; border-radius: 5px; font-size: 12px; font-weight: 600; }
.badge-risiko.rendah { background: #d1fae5; color: #065f46; }
.badge-risiko.sedang { background: #fef3c7; color: #92400e; }
.badge-risiko.tinggi { background: #fee2e2; color: #991b1b; }

.badge-permit { display: inline-block; padding: 3px 8px; border-radius: 5px; font-size: 12px; font-weight: 600; }
.badge-permit.ada { background: #dbeafe; color: #1d4ed8; }
.badge-permit.tidak { background: #f1f5f9; color: #64748b; }

.col-actions { display: flex; gap: 6px; }
.btn-icon { width: 30px; height: 30px; border: none; border-radius: 6px; background: #f1f5f9; color: #64748b; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: background 0.15s; }
.btn-icon svg { width: 14px; height: 14px; }
.btn-icon:hover { background: #e2e8f0; }
.btn-icon.danger:hover { background: #fee2e2; color: #dc2626; }

/* Modal */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 1000; display: flex; align-items: center; justify-content: center; padding: 20px; }
.modal { background: #fff; border-radius: 14px; width: 100%; max-width: 800px; max-height: 90vh; display: flex; flex-direction: column; overflow: hidden; }
.modal-sm { max-width: 400px; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 1px solid #e5e7eb; }
.modal-header h2 { font-size: 17px; font-weight: 700; color: #1e293b; margin: 0; }
.btn-close { background: none; border: none; font-size: 18px; color: #94a3b8; cursor: pointer; padding: 0 4px; }
.btn-close:hover { color: #475569; }
.modal-footer { display: flex; justify-content: flex-end; gap: 10px; padding: 16px 24px; border-top: 1px solid #e5e7eb; }

/* Form */
.modal-form { display: flex; flex-direction: column; overflow: hidden; }
.form-scroll { padding: 20px 24px; overflow-y: auto; display: flex; flex-direction: column; gap: 14px; }
.form-section-title { font-size: 12px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em; padding-bottom: 6px; border-bottom: 1px solid #f1f5f9; margin-top: 4px; }
.form-row { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 14px; }
.form-group { display: flex; flex-direction: column; gap: 5px; }
.form-group label { font-size: 13px; font-weight: 600; color: #374151; }
.form-group input, .form-group select { border: 1px solid #d1d5db; border-radius: 7px; padding: 8px 11px; font-size: 14px; color: #1e293b; background: #fff; outline: none; transition: border-color 0.15s; }
.form-group input:focus, .form-group select:focus { border-color: #3b82f6; }
.field-auto { background: #f1f5f9 !important; color: #64748b !important; cursor: not-allowed !important; border-color: #e2e8f0 !important; }
.field-auto-tag { font-size: 10px; font-weight: 600; color: #fff; background: #64748b; border-radius: 4px; padding: 1px 5px; margin-left: 5px; vertical-align: middle; }
.req { color: #ef4444; }
.form-error { margin: 0 24px; padding: 10px 14px; background: #fee2e2; color: #991b1b; border-radius: 7px; font-size: 13px; }
.form-warning { margin: 0 24px; padding: 10px 14px; background: #fef3c7; color: #92400e; border-radius: 7px; font-size: 13px; }
.foto-label-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px; }
.foto-label-row label { margin-bottom: 0; }
.btn-clear-fotos { background: none; border: 1px solid #fca5a5; color: #ef4444; border-radius: 6px; padding: 3px 10px; font-size: 12px; cursor: pointer; transition: background 0.15s; }
.btn-clear-fotos:hover { background: #fee2e2; }
.photo-count-label { font-size: 12px; font-weight: 600; color: #64748b; margin-left: 4px; }

/* Toggle */
.toggle-row { display: flex; align-items: center; gap: 10px; padding-top: 4px; }
.toggle { position: relative; display: inline-block; width: 40px; height: 22px; }
.toggle input { opacity: 0; width: 0; height: 0; }
.toggle-slider { position: absolute; inset: 0; background: #d1d5db; border-radius: 22px; cursor: pointer; transition: background 0.2s; }
.toggle-slider::before { content: ''; position: absolute; height: 16px; width: 16px; left: 3px; bottom: 3px; background: #fff; border-radius: 50%; transition: transform 0.2s; }
.toggle input:checked + .toggle-slider { background: #3b82f6; }
.toggle input:checked + .toggle-slider::before { transform: translateX(18px); }
.toggle-label { font-size: 14px; color: #374151; }

/* Bullet list */
.bullet-list { display: flex; flex-direction: column; gap: 6px; }
.bullet-row { display: flex; align-items: center; gap: 8px; }
.bullet-dot { font-weight: 700; color: #64748b; min-width: 20px; text-align: right; flex-shrink: 0; }
.bullet-row input { flex: 1; border: 1px solid #d1d5db; border-radius: 7px; padding: 7px 10px; font-size: 14px; outline: none; }
.bullet-row input:focus { border-color: #3b82f6; }
.btn-remove-bullet { background: none; border: none; color: #94a3b8; cursor: pointer; font-size: 13px; padding: 4px; border-radius: 4px; line-height: 1; }
.btn-remove-bullet:hover { color: #ef4444; background: #fee2e2; }
.btn-remove-bullet:disabled { opacity: 0.3; cursor: not-allowed; }
.btn-add-bullet { align-self: flex-start; background: none; border: 1px dashed #cbd5e1; color: #64748b; border-radius: 6px; padding: 5px 12px; font-size: 13px; cursor: pointer; margin-top: 2px; }
.btn-add-bullet:hover { background: #f8fafc; border-color: #94a3b8; }

/* Foto upload */
.foto-upload-area { display: flex; flex-direction: column; gap: 10px; }
.foto-preview-grid { display: flex; flex-wrap: wrap; gap: 10px; }
.foto-preview-item { position: relative; width: 90px; height: 90px; border-radius: 8px; overflow: hidden; border: 1px solid #e2e8f0; }
.foto-preview-item img { width: 100%; height: 100%; object-fit: cover; }
.btn-remove-foto { position: absolute; top: 3px; right: 3px; background: rgba(0,0,0,0.55); color: #fff; border: none; border-radius: 50%; width: 20px; height: 20px; font-size: 11px; cursor: pointer; display: flex; align-items: center; justify-content: center; }
.foto-add-btn { width: 90px; height: 90px; border: 2px dashed #cbd5e1; border-radius: 8px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 5px; cursor: pointer; color: #94a3b8; font-size: 11px; transition: border-color 0.15s, color 0.15s; }
.foto-add-btn:hover { border-color: #3b82f6; color: #3b82f6; }
.foto-add-btn.uploading { opacity: 0.6; cursor: not-allowed; }
.foto-add-btn svg { width: 22px; height: 22px; }

/* View body */
.view-body { display: flex; flex-direction: column; overflow: hidden; }
.view-scroll { padding: 16px 24px; overflow-y: auto; display: flex; flex-direction: column; gap: 14px; flex: 1; }

/* Banner */
.view-banner { position: relative; width: 100%; height: 200px; overflow: hidden; cursor: zoom-in; flex-shrink: 0; background: #0f172a; }
.view-banner img { width: 100%; height: 100%; object-fit: cover; opacity: 0.9; }
.view-banner-count { position: absolute; bottom: 10px; right: 12px; background: rgba(0,0,0,0.6); color: #fff; font-size: 12px; font-weight: 600; padding: 3px 10px; border-radius: 20px; }

/* Meta grid: 3 columns */
.view-meta-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px 16px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px 16px; }
.view-meta-item { display: flex; flex-direction: column; gap: 2px; }
.view-label { font-size: 10px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.06em; }
.view-val { font-size: 13px; color: #1e293b; font-weight: 500; }

/* 2-column detail layout */
.view-detail-cols { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.view-detail-col { display: flex; flex-direction: column; gap: 12px; }
.view-section { display: flex; flex-direction: column; gap: 6px; }
.view-section-label { font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px; margin-bottom: 2px; }
.view-bullets { margin: 0; padding-left: 18px; display: flex; flex-direction: column; gap: 3px; }
.view-bullets li { font-size: 13px; color: #374151; }

/* Foto grid */
.foto-grid { display: flex; flex-wrap: wrap; gap: 10px; }
.foto-thumb { width: 90px; height: 90px; object-fit: cover; border-radius: 8px; cursor: pointer; border: 1px solid #e2e8f0; transition: opacity 0.15s; }
.foto-thumb:hover { opacity: 0.85; }

/* Lightbox */
.lightbox { position: fixed; inset: 0; background: rgba(0,0,0,0.88); z-index: 2000; display: flex; align-items: center; justify-content: center; outline: none; }
.lightbox img { max-width: 88vw; max-height: 85vh; border-radius: 8px; object-fit: contain; user-select: none; }
.lb-close { position: absolute; top: 16px; right: 20px; background: rgba(255,255,255,0.15); border: none; color: #fff; font-size: 20px; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: background 0.15s; z-index: 1; }
.lb-close:hover { background: rgba(255,255,255,0.3); }
.lb-nav { position: absolute; top: 50%; transform: translateY(-50%); background: rgba(255,255,255,0.15); border: none; color: #fff; width: 48px; height: 48px; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: background 0.15s; z-index: 1; padding: 0; }
.lb-nav svg { width: 22px; height: 22px; display: block; }
.lb-nav:hover { background: rgba(255,255,255,0.3); }
.lb-prev { left: 20px; }
.lb-next { right: 20px; }
.lb-dots { position: absolute; bottom: 24px; left: 50%; transform: translateX(-50%); display: flex; gap: 8px; }
.lb-dot { width: 8px; height: 8px; border-radius: 50%; background: rgba(255,255,255,0.4); cursor: pointer; transition: background 0.15s; }
.lb-dot.active { background: #fff; }

/* Delete modal */
.delete-msg { padding: 16px 24px 0; font-size: 14px; color: #374151; margin: 0; }
</style>
