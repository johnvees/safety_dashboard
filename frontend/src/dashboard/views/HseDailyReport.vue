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
      <!-- Table header with title + export -->
      <div class="table-header">
        <h3>Data Laporan</h3>
        <div class="table-header-actions">
          <div class="export-dropdown-wrap" v-click-outside="() => showExportDropdown = false">
            <button class="btn btn-sm btn-export" @click="showExportDropdown = !showExportDropdown" title="Pilih format export">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
              Export
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="10" height="10" style="margin-left:2px"><polyline points="6 9 12 15 18 9"/></svg>
            </button>
            <div v-if="showExportDropdown" class="export-dropdown-menu">
              <button class="export-dropdown-item" @click="exportCsvAll(); showExportDropdown = false" :disabled="filteredRecords.length === 0">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
                <div>
                  <div class="export-item-label">CSV (Semua Data)</div>
                  <div class="export-item-desc">Export data yang tampil saat ini</div>
                </div>
              </button>
              <button class="export-dropdown-item" @click="showHseExportModal = true; showExportDropdown = false">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                <div>
                  <div class="export-item-label">Laporan Bulanan</div>
                  <div class="export-item-desc">Export CSV atau PDF per bulan</div>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
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
            <th style="width:48px;text-align:center;">No</th>
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
          <tr v-for="(r, idx) in pagedRecords" :key="r.id" @click="openView(r)" class="row-clickable">
            <td style="text-align:center;">{{ (hseCurrentPage - 1) * hsePerPage + idx + 1 }}</td>
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
          <tr v-if="pagedRecords.length === 0">
            <td colspan="9" class="no-results">Tidak ada data yang cocok</td>
          </tr>
        </tbody>
      </table>
      </div>
      <PaginationBar
        :current-page="hseCurrentPage"
        :total-pages="hseTotalPages"
        :total-items="hseTotalItems"
        :per-page="hsePerPage"
        @page="hseGoToPage"
        @per-page="hseSetPerPage"
      />
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
                <input type="datetime-local" v-model="form.tanggal" required class="input-date" @click="$event.target.showPicker?.()" />
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
              <label>Foto <span class="photo-count-label">({{ form.fotos.length }}/10)</span></label>
              <div class="photo-upload">
                <div class="photo-grid" v-if="form.fotos.length > 0">
                  <div class="photo-preview" v-for="(photo, i) in form.fotos" :key="i">
                    <img :src="photo.preview" alt="Preview" />
                    <button type="button" class="photo-remove" @click="removeFoto(i)">✕</button>
                  </div>
                </div>
                <div class="photo-clear" v-if="form.fotos.length > 1">
                  <button type="button" class="btn btn-clear" @click="clearFotos">Hapus Semua Foto</button>
                </div>
                <div class="photo-actions" v-if="form.fotos.length < 10">
                  <label class="photo-btn">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
                      <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                      <circle cx="8.5" cy="8.5" r="1.5"/>
                      <polyline points="21 15 16 10 5 21"/>
                    </svg>
                    Galeri
                    <input type="file" accept="image/*" multiple @change="onFotoSelect" style="display:none" />
                  </label>
                  <label class="photo-btn">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
                      <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
                      <circle cx="12" cy="13" r="4"/>
                    </svg>
                    Kamera
                    <input type="file" accept="image/*" capture="environment" @change="onFotoSelect" style="display:none" />
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
    <!-- Modal: Export Bulanan HSE -->
    <div v-if="showHseExportModal" class="modal-overlay" @mousedown.self="showHseExportModal = false">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h3 class="modal-title">Export Data Bulanan</h3>
          <button class="modal-close" @click="showHseExportModal = false">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>
        <div class="modal-body">
          <p class="modal-desc">Pilih bulan dan tahun untuk export data HSE Daily Report.</p>
          <div class="export-month-row">
            <div class="export-field">
              <label class="export-label">Bulan</label>
              <select v-model="hseExportMonth" class="export-select">
                <option v-for="(name,idx) in MONTH_NAMES" :key="idx+1" :value="idx+1">{{ name }}</option>
              </select>
            </div>
            <div class="export-field">
              <label class="export-label">Tahun</label>
              <select v-model="hseExportYear" class="export-select">
                <option v-for="y in yearOptions" :key="y" :value="y">{{ y }}</option>
              </select>
            </div>
          </div>
          <div class="export-preview-text">
            Export data bulan <strong>{{ MONTH_NAMES[hseExportMonth-1] }} {{ hseExportYear }}</strong>
          </div>
        </div>
        <div class="modal-footer-bar">
          <button class="btn-secondary" @click="showHseExportModal = false">Batal</button>
          <div class="export-btn-group">
            <button class="btn btn-export-csv" @click="exportMonthlyCSV" title="Download sebagai file CSV">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
              CSV
            </button>
            <button class="btn btn-export-pdf" @click="downloadMonthlyPDF" :disabled="pdfGenerating" title="Download sebagai file PDF">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
              {{ pdfGenerating ? 'Generating...' : 'PDF' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue';
import { authService } from '@/services/authService.js';
import { hseDailyService, uploadImage } from '@/services/hseDailyService.js';
import { usePagination } from '@/composables/usePagination.js';
import PaginationBar from '@/components/PaginationBar.vue';
import { exportToCsv } from '@/services/exportCsvService.js';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

const vClickOutside = {
  mounted(el, binding) {
    el._clickOutsideHandler = (e) => { if (!el.contains(e.target)) binding.value(e); };
    document.addEventListener('mousedown', el._clickOutsideHandler);
  },
  unmounted(el) { document.removeEventListener('mousedown', el._clickOutsideHandler); },
};

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

const {
  currentPage: hseCurrentPage,
  perPage: hsePerPage,
  totalItems: hseTotalItems,
  totalPages: hseTotalPages,
  paginatedItems: pagedRecords,
  goToPage: hseGoToPage,
  setPerPage: hseSetPerPage,
} = usePagination(filteredRecords);

let photoWarnTimer = null;
function showPhotoWarning(msg) {
  photoWarning.value = msg;
  if (photoWarnTimer) clearTimeout(photoWarnTimer);
  photoWarnTimer = setTimeout(() => { photoWarning.value = ''; }, 3500);
}

const modal = ref({ open: false, mode: 'create', record: null });

const defaultForm = () => ({
  tanggal: '',
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
    tanggal: record.tanggal ? record.tanggal.replace(' ', 'T').slice(0, 16) : '',
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
  const dt = new Date(d.replace ? d.replace(' ', 'T') : d);
  if (isNaN(dt)) return '-';
  const date = dt.toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' });
  const time = dt.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' });
  return `${date} ${time}`;
}

function formatDateFull(d) {
  if (!d) return '-';
  const dt = new Date(d.replace ? d.replace(' ', 'T') : d);
  if (isNaN(dt)) return '-';
  const date = dt.toLocaleDateString('id-ID', { weekday: 'long', day: '2-digit', month: 'long', year: 'numeric' });
  const time = dt.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' });
  return `${date}, ${time}`;
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

// ── Export ─────────────────────────────────────────────────────────────────
const MONTH_NAMES = ['Januari','Februari','Maret','April','Mei','Juni','Juli','Agustus','September','Oktober','November','Desember'];
const showExportDropdown = ref(false);
const showHseExportModal = ref(false);
const hseExportMonth = ref(new Date().getMonth() + 1);
const hseExportYear = ref(new Date().getFullYear());
const pdfGenerating = ref(false);

const yearOptions = computed(() => {
  const yr = new Date().getFullYear();
  return Array.from({ length: 5 }, (_, i) => yr - i);
});

const CSV_COLUMNS = [
  { label: 'No',               key: 'no' },
  { label: 'Tanggal',          key: 'tanggal' },
  { label: 'Lokasi Pekerjaan', key: 'lokasiPekerjaan' },
  { label: 'Jenis Pekerjaan',  key: 'jenisPekerjaan' },
  { label: 'Level Risiko',     key: 'levelRisiko' },
  { label: 'Pengawas HSE',     key: 'pengawasHse' },
  { label: 'Permit',           key: 'statusPermit' },
  { label: 'Pekerjaan',        key: 'pekerjaan' },
  { label: 'Potensi Bahaya',   key: 'potensiBahaya' },
  { label: 'Pengendalian',     key: 'pengendalianBahaya' },
  { label: 'Saran/Masukan',    key: 'saranMasukan' },
];

function recordsToCsvRows(rows) {
  return rows.map((r, i) => ({
    no: i + 1,
    tanggal: r.tanggal || '',
    lokasiPekerjaan: r.lokasiPekerjaan || '',
    jenisPekerjaan: displayJenis(r),
    levelRisiko: r.levelRisiko || '',
    pengawasHse: r.pengawasHse || '',
    statusPermit: r.statusPermit ? 'Ada' : 'Tidak',
    pekerjaan: parseBullets(r.pekerjaan).join(' | '),
    potensiBahaya: parseBullets(r.potensiBahaya).join(' | '),
    pengendalianBahaya: parseBullets(r.pengendalianBahaya).join(' | '),
    saranMasukan: parseBullets(r.saranMasukan).join(' | '),
  }));
}

function exportCsvAll() {
  const today = new Date().toISOString().slice(0, 10);
  exportToCsv(`hse-daily-${today}.csv`, CSV_COLUMNS, recordsToCsvRows(filteredRecords.value));
}

function exportMonthlyCSV() {
  const m = hseExportMonth.value;
  const y = hseExportYear.value;
  const rows = records.value.filter(r => {
    if (!r.tanggal) return false;
    const d = new Date(r.tanggal);
    return d.getFullYear() === y && d.getMonth() + 1 === m;
  });
  if (!rows.length) { alert(`Tidak ada data untuk ${MONTH_NAMES[m-1]} ${y}.`); return; }
  exportToCsv(`hse-daily-${y}-${String(m).padStart(2,'0')}.csv`, CSV_COLUMNS, recordsToCsvRows(rows));
  showHseExportModal.value = false;
}

async function downloadMonthlyPDF() {
  const m = hseExportMonth.value;
  const y = hseExportYear.value;
  const monthRows = records.value.filter(r => {
    if (!r.tanggal) return false;
    const d = new Date(r.tanggal);
    return d.getFullYear() === y && d.getMonth() + 1 === m;
  });
  if (!monthRows.length) { alert(`Tidak ada data untuk ${MONTH_NAMES[m-1]} ${y}.`); return; }

  pdfGenerating.value = true;
  await nextTick();
  try {
    const doc = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' });
    const pageW = doc.internal.pageSize.getWidth();
    const dark = [30, 41, 59];

    // Header
    doc.setFillColor(30, 41, 59);
    doc.rect(0, 0, pageW, 22, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.text('HSE DAILY REPORT', pageW / 2, 10, { align: 'center' });
    doc.setFontSize(9);
    doc.setFont('helvetica', 'normal');
    doc.text(`PT Charoen Pokphand Indonesia  |  Periode: ${MONTH_NAMES[m-1]} ${y}`, pageW / 2, 17, { align: 'center' });

    // Summary stats
    const total    = monthRows.length;
    const rendah   = monthRows.filter(r => r.levelRisiko === 'Rendah').length;
    const sedang   = monthRows.filter(r => r.levelRisiko === 'Sedang').length;
    const tinggi   = monthRows.filter(r => r.levelRisiko === 'Tinggi').length;
    const withPermit = monthRows.filter(r => r.statusPermit).length;

    const stats = [
      { label: 'Total Laporan', value: total },
      { label: 'Risiko Rendah', value: rendah },
      { label: 'Risiko Sedang', value: sedang },
      { label: 'Risiko Tinggi', value: tinggi },
      { label: 'Dengan Permit', value: withPermit },
    ];
    const boxW = (pageW - 28) / stats.length;
    let bx = 14;
    stats.forEach(s => {
      doc.setFillColor(241, 245, 249);
      doc.setDrawColor(203, 213, 225);
      doc.roundedRect(bx, 26, boxW - 2, 14, 2, 2, 'FD');
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(13);
      doc.setTextColor(...dark);
      doc.text(String(s.value), bx + (boxW - 2) / 2, 31, { align: 'center' });
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(7);
      doc.setTextColor(100, 116, 139);
      doc.text(s.label, bx + (boxW - 2) / 2, 36.5, { align: 'center' });
      bx += boxW;
    });

    // Main data table
    const tableRows = monthRows.map((r, i) => [
      i + 1,
      r.tanggal || '',
      r.lokasiPekerjaan || '-',
      displayJenis(r),
      r.levelRisiko || '-',
      r.pengawasHse || '-',
      r.statusPermit ? 'Ada' : 'Tidak',
      parseBullets(r.pekerjaan).join('\n'),
      parseBullets(r.potensiBahaya).join('\n'),
      parseBullets(r.pengendalianBahaya).join('\n'),
    ]);

    autoTable(doc, {
      startY: 44,
      head: [['No','Tanggal','Lokasi','Jenis Pekerjaan','Level Risiko','Pengawas HSE','Permit','Pekerjaan','Potensi Bahaya','Pengendalian']],
      body: tableRows,
      theme: 'grid',
      headStyles: { fillColor: [30,41,59], textColor: 255, fontSize: 7.5, fontStyle: 'bold', halign: 'center' },
      bodyStyles: { fontSize: 7.5, textColor: dark, valign: 'top' },
      columnStyles: {
        0: { cellWidth: 8,  halign: 'center' },
        1: { cellWidth: 20, halign: 'center' },
        2: { cellWidth: 28 },
        3: { cellWidth: 28 },
        4: { cellWidth: 20, halign: 'center' },
        5: { cellWidth: 28 },
        6: { cellWidth: 15, halign: 'center' },
        7: { cellWidth: 42 },
        8: { cellWidth: 42 },
        9: { cellWidth: 42 },
      },
      margin: { left: 14, right: 14 },
      didParseCell(data) {
        if (data.section === 'body' && data.column.index === 4) {
          const v = data.cell.raw;
          if (v === 'Rendah') data.cell.styles.textColor = [22, 163, 74];
          else if (v === 'Sedang') data.cell.styles.textColor = [217, 119, 6];
          else if (v === 'Tinggi') data.cell.styles.textColor = [220, 38, 38];
        }
      },
    });

    // Breakdown per Risiko
    const risikoY = doc.lastAutoTable.finalY + 8;
    doc.setTextColor(...dark);
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    doc.text('BREAKDOWN PER LEVEL RISIKO', 14, risikoY);

    const risikoRows = ['Rendah','Sedang','Tinggi'].map(lv => {
      const rows = monthRows.filter(r => r.levelRisiko === lv);
      const withP = rows.filter(r => r.statusPermit).length;
      const pct = rows.length > 0 ? `${Math.round((withP / rows.length) * 100)}%` : '-';
      return [lv, rows.length, withP, rows.length - withP, pct];
    });

    autoTable(doc, {
      startY: risikoY + 3,
      head: [['Level Risiko','Jumlah','Dengan Permit','Tanpa Permit','% Permit']],
      body: risikoRows,
      theme: 'striped',
      headStyles: { fillColor: [71,85,105], textColor: 255, fontSize: 8, fontStyle: 'bold', halign: 'center' },
      bodyStyles: { fontSize: 9, halign: 'center' },
      columnStyles: { 0: { halign: 'left', fontStyle: 'bold' } },
      margin: { left: 14, right: 14 },
    });

    doc.save(`hse-daily-${y}-${String(m).padStart(2,'0')}.pdf`);
    showHseExportModal.value = false;
  } finally {
    pdfGenerating.value = false;
  }
}
</script>

<style scoped>
/* Page */
.page { padding: var(--sp-8) var(--sp-8); display: flex; flex-direction: column; gap: var(--sp-5); }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; }
.page-title { font-size: 22px; font-weight: 700; color: #1e293b; margin: 0 0 4px; }
.page-sub { font-size: 13px; color: #64748b; margin: 0; }

/* Table */
.table-card table { min-width: 800px; }
.table-scroll { overflow-x: auto; -webkit-overflow-scrolling: touch; }
.loading { padding: 40px; text-align: center; color: #94a3b8; }
.table-toolbar { padding: 12px 20px; }
.search-box { display: flex; align-items: center; gap: 8px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0 10px; flex: 1; min-width: 200px; }
.search-box svg { width: 16px; height: 16px; color: #94a3b8; flex-shrink: 0; }
.search-box input { border: none; background: transparent; font-size: 13px; color: #1e293b; outline: none; flex: 1; padding: 8px 0; }
.search-box input::placeholder { color: #94a3b8; }
.search-clear { background: none; border: none; color: #94a3b8; cursor: pointer; font-size: 13px; padding: 0; line-height: 1; }
.search-clear:hover { color: #64748b; }
.btn-reset-filter { background: none; border: 1px solid #fca5a5; color: #ef4444; border-radius: 8px; font-size: 12px; padding: 7px 12px; cursor: pointer; white-space: nowrap; }
.btn-reset-filter:hover { background: #fee2e2; }
.date-filter-row { padding: 10px 20px; }
.date-chip { background: #f1f5f9; border: 1px solid transparent; border-radius: 20px; padding: 5px 14px; font-size: 13px; color: #64748b; cursor: pointer; transition: all 0.15s; white-space: nowrap; }
.date-chip:hover { background: #e2e8f0; color: #1e293b; }
.date-chip.active { background: #3b82f6; color: #fff; border-color: #3b82f6; }
.toolbar-date-wrap { display: inline-flex; border: 1px solid #cbd5e1; border-radius: 8px; background: #fff; overflow: hidden; cursor: pointer; transition: border-color 0.15s; }
.toolbar-date-wrap:focus-within { border-color: #3b82f6; }
.toolbar-date { border: none; background: transparent; color: #1e293b; font-size: 13px; padding: 6px 10px; outline: none; cursor: pointer; color-scheme: light; width: 140px; }
.date-sep { color: #94a3b8; font-size: 13px; }
.no-results { text-align: center; padding: 32px; color: #94a3b8; font-size: 14px; }
th { text-transform: uppercase; letter-spacing: 0.04em; }
.row-clickable { cursor: pointer; transition: background 0.1s; }
.col-pekerjaan { max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.badge-risiko { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.badge-risiko.rendah { background: #d1fae5; color: #065f46; }
.badge-risiko.sedang { background: #fef3c7; color: #92400e; }
.badge-risiko.tinggi { background: #fee2e2; color: #991b1b; }

.badge-permit { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.badge-permit.ada { background: #dbeafe; color: #1d4ed8; }
.badge-permit.tidak { background: #f1f5f9; color: #64748b; }

.col-actions { display: flex; gap: 6px; }

/* Form */
.modal-form { display: flex; flex-direction: column; overflow: hidden; }
.form-scroll { padding: var(--sp-5) var(--sp-6); overflow-y: auto; display: flex; flex-direction: column; gap: 14px; }
.form-section-title { font-size: 12px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em; padding-bottom: 6px; border-bottom: 1px solid #f1f5f9; margin-top: 4px; }
.form-row { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 14px; }
.form-group { display: flex; flex-direction: column; gap: 5px; }
.form-group label { font-size: 13px; font-weight: 600; color: #374151; }
.form-group input, .form-group select { border: 1px solid #e2e8f0; border-radius: 8px; padding: 9px 12px; font-size: 14px; color: #1e293b; background: #fff; outline: none; transition: border-color 0.15s, box-shadow 0.15s; }
.form-group input:focus, .form-group select:focus { border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.12); }
.field-auto { background: #f1f5f9 !important; color: #64748b !important; cursor: not-allowed !important; border-color: #e2e8f0 !important; }
.field-auto-tag { font-size: 10px; font-weight: 600; color: #fff; background: #64748b; border-radius: 4px; padding: 1px 5px; margin-left: 5px; vertical-align: middle; }
.req { color: #ef4444; }
.input-date { cursor: pointer; color-scheme: light; }
.form-error { margin: 0 24px; padding: 10px 14px; background: #fee2e2; color: #991b1b; border-radius: 7px; font-size: 13px; }
.form-warning { margin: 0 24px; padding: 10px 14px; background: #fef3c7; color: #92400e; border-radius: 7px; font-size: 13px; }
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
.bullet-row input { flex: 1; border: 1px solid #e2e8f0; border-radius: 8px; padding: 9px 12px; font-size: 14px; outline: none; transition: border-color 0.15s, box-shadow 0.15s; }
.bullet-row input:focus { border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.12); }
.btn-remove-bullet { background: none; border: none; color: #94a3b8; cursor: pointer; font-size: 13px; padding: 4px; border-radius: 4px; line-height: 1; }
.btn-remove-bullet:hover { color: #ef4444; background: #fee2e2; }
.btn-remove-bullet:disabled { opacity: 0.3; cursor: not-allowed; }
.btn-add-bullet { align-self: flex-start; background: none; border: 1px dashed #cbd5e1; color: #64748b; border-radius: 6px; padding: 5px 12px; font-size: 13px; cursor: pointer; margin-top: 2px; }
.btn-add-bullet:hover { background: #f8fafc; border-color: #94a3b8; }

/* Foto upload */
.photo-upload { border: 2px dashed #e2e8f0; border-radius: 8px; padding: 16px; }
.photo-grid { display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 12px; }
.photo-preview { position: relative; display: inline-block; }
.photo-preview img { width: 100px; height: 100px; border-radius: 8px; object-fit: cover; border: 1px solid #e2e8f0; }
.photo-remove { position: absolute; top: -6px; right: -6px; width: 20px; height: 20px; border-radius: 50%; background: #ef4444; color: #fff; border: none; font-size: 11px; font-weight: 700; cursor: pointer; display: flex; align-items: center; justify-content: center; }
.photo-actions { display: flex; gap: 12px; justify-content: center; }
.photo-btn { display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 12px 20px; border-radius: 8px; background: #f8fafc; border: 1px solid #e2e8f0; color: #475569; font-size: 13px; font-weight: 600; cursor: pointer; transition: background 0.15s, border-color 0.15s; }
.photo-btn:hover { background: #f1f5f9; border-color: #3b82f6; color: #3b82f6; }
.photo-clear { margin-top: 8px; }
.btn-clear { padding: 6px 12px; font-size: 12px; font-weight: 600; background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; border-radius: 6px; cursor: pointer; }

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

/* Export button (green tint, unique to this page) */
.btn-export {
  display: inline-flex; align-items: center; gap: 5px;
  background: #f0fdf4; color: #166534; border: 1px solid #bbf7d0;
  border-radius: var(--r-sm); padding: 7px 12px; font-size: 13px; font-weight: 500;
  cursor: pointer; white-space: nowrap; transition: background 0.15s;
}
.btn-export:hover { background: #dcfce7; border-color: #86efac; }
.modal-title { font-size: 16px; font-weight: 700; color: #1e293b; margin: 0; }
.modal-close {
  display: inline-flex; align-items: center; justify-content: center;
  width: 30px; height: 30px; border-radius: 6px; border: none;
  background: transparent; color: #94a3b8; cursor: pointer; transition: background 0.15s, color 0.15s;
}
.modal-close:hover { background: #f1f5f9; color: #1e293b; }
.export-preview-text {
  margin-top: 4px; font-size: 13px; color: #374151;
  background: #f0f9ff; border: 1px solid #bae6fd;
  border-radius: var(--r-md); padding: 9px 14px;
}
.modal-footer-bar {
  display: flex; align-items: center; justify-content: flex-end;
  gap: 10px; padding: 14px 24px 18px;
  border-top: 1px solid #e2e8f0; background: #f8fafc;
  border-radius: 0 0 14px 14px; flex-shrink: 0;
}
.export-btn-group { display: flex; gap: 8px; }
.btn-export-csv {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 8px 16px; background: #f0fdf4; color: #15803d;
  border: 1.5px solid #86efac; border-radius: 7px;
  font-size: 13px; font-weight: 600; cursor: pointer; transition: background 0.15s, border-color 0.15s;
}
.btn-export-csv:hover { background: #dcfce7; border-color: #4ade80; }
.btn-export-pdf {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 8px 16px; background: #7c3aed; color: #fff;
  border: 1.5px solid #7c3aed; border-radius: 7px;
  font-size: 13px; font-weight: 600; cursor: pointer; transition: background 0.15s;
}
.btn-export-pdf:hover:not(:disabled) { background: #6d28d9; border-color: #6d28d9; }
.btn-export-pdf:disabled { opacity: 0.6; cursor: not-allowed; }

/* Modal body */
</style>
