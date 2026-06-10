<template>
  <div class="case-incident">
    <div class="page-header">
      <div>
        <h2>Case Incident</h2>
        <p class="subtitle">Laporan insiden &amp; kecelakaan kerja</p>
      </div>
      <button class="btn-primary" @click="openForm">+ Tambah Laporan</button>
    </div>

    <div class="table-card">
      <!-- Data header with export -->
      <div class="table-header">
        <h3>Data Laporan</h3>
        <div class="table-header-actions">
          <button
            class="btn btn-sm btn-export"
            @click="exportExcel"
            :disabled="filteredRecords.length === 0"
            title="Ekspor data ke Excel"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="7 10 12 15 17 10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>
            Ekspor
          </button>
        </div>
      </div>

      <!-- Date filter row -->
      <div class="date-filter-row">
        <button
          v-for="opt in DATE_PRESETS"
          :key="opt.value"
          class="date-chip"
          :class="{ active: filterDate === opt.value }"
          @click="setDatePreset(opt.value)"
        >
          {{ opt.label }}
        </button>
      </div>
      <div v-if="filterDate === 'custom'" class="custom-date-row">
        <label class="toolbar-date-wrap">
          <input type="date" v-model="customDateFrom" class="toolbar-date" @click="$event.target.showPicker?.()" />
        </label>
        <span class="date-sep">–</span>
        <label class="toolbar-date-wrap">
          <input type="date" v-model="customDateTo" class="toolbar-date" @click="$event.target.showPicker?.()" />
        </label>
      </div>

      <!-- Filter bar -->
      <div class="filter-bar">
      <div class="search-wrapper">
        <svg
          class="search-icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          width="15"
          height="15"
        >
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
        <input
          type="text"
          v-model="searchQuery"
          class="search-input"
          placeholder="Cari korban, pelapor, lokasi..."
        />
        <button
          v-if="searchQuery"
          class="search-clear"
          @click="searchQuery = ''"
        >
          &times;
        </button>
      </div>

      <select v-model="filterJenis" class="filter-select">
        <option value="">Semua Jenis</option>
        <option value="Near Miss">Near Miss</option>
        <option value="P3K">P3K</option>
        <option value="Medical Treatment">Medical Treatment</option>
        <option value="LTI (Lost Time Injury)">LTI (Lost Time Injury)</option>
        <option value="Fire">Fire</option>
        <option value="Explosion">Explosion</option>
        <option value="Konsleting Listrik">Konsleting Listrik</option>
        <option value="Kerusakan Properti">Kerusakan Properti</option>
        <option value="Kecelakaan Transportasi">Kecelakaan Transportasi</option>
        <option value="Fatality">Fatality</option>
        <option value="Pencemaran / Polusi Lingkungan">
          Pencemaran / Polusi Lingkungan
        </option>
      </select>

      <select v-model="filterStatus" class="filter-select">
        <option value="">Semua Status</option>
        <option value="Open">Open</option>
        <option value="In Progress">In Progress</option>
        <option value="Closed">Closed</option>
      </select>

      <button
        v-if="hasActiveFilters"
        class="btn-reset-filters"
        @click="resetFilters"
      >
        Reset
      </button>
      <span v-if="hasActiveFilters" class="filter-count"
        >{{ filteredRecords.length }} / {{ records.length }} data</span
      >
    </div>

    <!-- Table -->
    <div class="table-wrapper">
      <div v-if="loading" class="ci-loading">
        <div class="ci-spinner"></div>
        <span>Memuat data…</span>
      </div>
      <table v-else-if="pagedRecords.length > 0">
        <thead>
          <tr>
            <th style="text-align: center; width: 48px">No</th>
            <th>Aksi</th>
            <th>Tanggal Kejadian</th>
            <th>Tanggal Pelaporan</th>
            <th>Business Unit</th>
            <th>Plant</th>
            <th>Nama Pelapor</th>
            <th>Nama Korban</th>
            <th>Status Karyawan</th>
            <th>Jenis Kecelakaan</th>
            <th>Lokasi</th>
            <th style="text-align: center">Foto</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(item, idx) in pagedRecords"
            :key="item.id"
            class="row-clickable"
            @click="viewRecord(item)"
          >
            <td style="text-align: center">
              {{ (ciCurrentPage - 1) * ciPerPage + idx + 1 }}
            </td>
            <td class="td-actions" @click.stop>
              <div class="actions-wrap">
                <button
                  class="btn-icon btn-danger"
                  title="Hapus"
                  @click="deleteRecord(item)"
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
              </div>
            </td>
            <td class="td-nowrap">{{ formatDate(item.tanggalKejadian) }}</td>
            <td class="td-nowrap">
              {{
                item.tanggalPelaporan ? formatDate(item.tanggalPelaporan) : '-'
              }}
            </td>
            <td class="td-nowrap">
              {{
                item.businessUnitName ||
                getBusinessUnitName(item.businessUnitId)
              }}
            </td>
            <td class="td-nowrap">
              {{ item.plantName || getPlantName(item.plantId) }}
            </td>
            <td class="td-nowrap">{{ item.namaPelapor || '-' }}</td>
            <td class="td-nowrap">{{ item.namaKorban || '-' }}</td>
            <td class="td-nowrap">{{ item.statusKaryawan || '-' }}</td>
            <td>
              <span
                :class="['jenis-badge', jenisClass(item.jenisKecelakaan)]"
                >{{ item.jenisKecelakaan || '-' }}</span
              >
            </td>
            <td class="td-truncate">{{ item.lokasiKecelakaan || '-' }}</td>
            <td style="text-align: center" @click.stop>
              <button
                v-if="parsePhotos(item.fotoKejadian).length"
                class="photo-count-badge photo-count-btn"
                @click="
                  openPhotoModalFromUrls(parsePhotos(item.fotoKejadian), 0)
                "
              >
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  width="13"
                  height="13"
                >
                  <path
                    d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"
                  />
                  <circle cx="12" cy="13" r="4" />
                </svg>
                {{ parsePhotos(item.fotoKejadian).length }}
              </button>
              <span v-else class="text-muted">-</span>
            </td>
            <td style="text-align: center">
              <span
                :class="[
                  'status-badge',
                  `status-${(item.status || 'open').toLowerCase().replace(' ', '-')}`,
                ]"
              >
                {{ item.status || 'Open' }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Mobile card list -->
      <div class="card-list" v-if="!loading && pagedRecords.length > 0">
        <div
          v-for="(item, idx) in pagedRecords"
          :key="item.id"
          class="row-card"
          @click="viewRecord(item)"
        >
          <div class="rc-head">
            <div>
              <div class="rc-title">{{ item.namaKorban || 'Tanpa nama korban' }}</div>
              <div class="rc-sub">{{ formatDate(item.tanggalKejadian) }}</div>
            </div>
            <span :class="['jenis-badge', jenisClass(item.jenisKecelakaan)]">{{ item.jenisKecelakaan || '-' }}</span>
          </div>
          <div class="rc-body">
            <div class="rc-row"><span class="rc-label">Pelapor</span><span class="rc-value">{{ item.namaPelapor || '-' }}</span></div>
            <div class="rc-row"><span class="rc-label">Lokasi</span><span class="rc-value">{{ item.lokasiKecelakaan || '-' }}</span></div>
            <div class="rc-row"><span class="rc-label">Plant</span><span class="rc-value">{{ item.plantName || getPlantName(item.plantId) }}</span></div>
            <div class="rc-row"><span class="rc-label">Status Karyawan</span><span class="rc-value">{{ item.statusKaryawan || '-' }}</span></div>
            <div class="rc-row" v-if="parsePhotos(item.fotoKejadian).length">
              <span class="rc-label">Foto</span>
              <span class="rc-value">
                <button class="photo-count-badge photo-count-btn" @click.stop="openPhotoModalFromUrls(parsePhotos(item.fotoKejadian), 0)">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13">
                    <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
                    <circle cx="12" cy="13" r="4"/>
                  </svg>
                  {{ parsePhotos(item.fotoKejadian).length }}
                </button>
              </span>
            </div>
          </div>
          <div class="rc-footer">
            <span :class="['status-badge', `status-${(item.status || 'open').toLowerCase().replace(' ', '-')}`]">{{ item.status || 'Open' }}</span>
            <div class="rc-actions" @click.stop>
              <button class="btn-icon btn-danger" title="Hapus" @click="deleteRecord(item)">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                  <polyline points="3 6 5 6 21 6"/>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <PaginationBar
        v-if="!loading && pagedRecords.length > 0"
        :current-page="ciCurrentPage"
        :total-pages="ciTotalPages"
        :total-items="ciTotalItems"
        :per-page="ciPerPage"
        @page="ciGoToPage"
        @per-page="ciSetPerPage"
      />
      <div v-else-if="!loading && hasActiveFilters" class="empty-state">
        <p>
          Tidak ada data yang cocok dengan filter.
          <button class="btn-inline-link" @click="resetFilters">
            Atur ulang filter
          </button>
        </p>
      </div>
      <div v-else-if="!loading" class="empty-state">
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
          width="48"
          height="48"
          style="color: #94a3b8; margin-bottom: 8px"
        >
          <path
            d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"
          />
        </svg>
        <p>
          Belum ada laporan insiden. Klik "+ Tambah Laporan" untuk menambahkan.
        </p>
      </div>
      </div>
    </div>

    <!-- ── Form Modal ── -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showForm" class="modal-overlay" @click.self="tryClose">
          <div class="modal-container modal-lg">
            <div class="modal-header">
              <h3 class="modal-title">
                {{ editingId ? 'Ubah Laporan' : 'Tambah Laporan Insiden' }}
              </h3>
              <button
                class="modal-close"
                type="button"
                @click="tryClose"
                aria-label="Tutup"
              >
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  width="20"
                  height="20"
                >
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            </div>

            <div class="modal-body">
              <form @submit.prevent="submitForm" class="form-grid" id="ci-form">
                <!-- ── Data Kecelakaan ── -->
                <div class="form-section">
                  <h4 class="section-title">Data Kecelakaan</h4>

                  <div class="form-row">
                    <div class="form-group">
                      <label>Nama Pelapor</label>
                      <input
                        type="text"
                        :value="
                          currentUser?.fullName || currentUser?.username || '-'
                        "
                        disabled
                        class="input-pelapor"
                      />
                    </div>
                    <div class="form-group">
                      <label>Dept. Pelapor</label>
                      <input
                        type="text"
                        :value="currentUser?.department || '-'"
                        disabled
                        class="input-pelapor"
                      />
                    </div>
                  </div>

                  <div class="form-row">
                    <div class="form-group">
                      <label>Business Unit</label>
                      <select v-model.number="form.businessUnitId" disabled>
                        <option :value="null">-- Pilih Business Unit --</option>
                        <option
                          v-for="bu in businessUnits"
                          :key="bu.id"
                          :value="bu.id"
                        >
                          {{ bu.name }}
                        </option>
                      </select>
                    </div>
                    <div class="form-group">
                      <label>Plant</label>
                      <select v-model.number="form.plantId" disabled>
                        <option :value="null">-- Pilih Plant --</option>
                        <option v-for="p in plants" :key="p.id" :value="p.id">
                          {{ p.name }}
                        </option>
                      </select>
                    </div>
                  </div>

                  <div
                    class="form-group form-group--full"
                    style="margin-top: 4px"
                  >
                    <label>Nama Saksi</label>
                    <div class="petugas-list">
                      <div
                        v-for="(saksi, idx) in saksiList"
                        :key="idx"
                        class="petugas-row"
                      >
                        <div class="petugas-nama-wrap">
                          <input
                            type="text"
                            v-model="saksi.nama"
                            @input="onSaksiInput(idx, $event)"
                            @keydown="onSaksiKeydown(idx, $event)"
                            @blur="onSaksiBlur(idx)"
                            placeholder="Nama saksi atau ketik @ untuk cari pengguna..."
                            class="petugas-nama-input"
                          />
                          <div
                            v-if="
                              saksiMentionActive === idx &&
                              saksiMentionResults.length
                            "
                            class="mention-dropdown"
                          >
                            <button
                              v-for="(u, mi) in saksiMentionResults"
                              :key="u.id"
                              type="button"
                              :class="[
                                'mention-item',
                                {
                                  'mention-item-active':
                                    saksiMentionHighlight === mi,
                                },
                              ]"
                              @mousedown.prevent="selectSaksiMention(idx, u)"
                            >
                              <span class="mention-name">{{
                                u.fullName || u.username
                              }}</span>
                              <span v-if="u.departmentId" class="mention-dept">
                                {{
                                  departments.find(
                                    (d) => d.id === u.departmentId,
                                  )?.name || ''
                                }}
                              </span>
                            </button>
                          </div>
                        </div>
                        <select
                          v-model.number="saksi.departmentId"
                          class="petugas-dept-select"
                        >
                          <option :value="null">Pilih Dept.</option>
                          <option
                            v-for="d in departments"
                            :key="d.id"
                            :value="d.id"
                          >
                            {{ d.name }}
                          </option>
                        </select>
                        <button
                          type="button"
                          class="petugas-remove"
                          @click="removeSaksi(idx)"
                          v-if="saksiList.length > 1"
                          title="Hapus"
                        >
                          ×
                        </button>
                      </div>
                    </div>
                    <button
                      type="button"
                      class="bullet-add"
                      @click="addSaksi"
                      style="margin-top: 8px"
                    >
                      <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2.5"
                        width="12"
                        height="12"
                      >
                        <line x1="12" y1="5" x2="12" y2="19" />
                        <line x1="5" y1="12" x2="19" y2="12" />
                      </svg>
                      Tambah Saksi
                    </button>
                  </div>

                  <div class="form-row">
                    <div class="form-group">
                      <label
                        >Tanggal Kejadian <span class="required">*</span></label
                      >
                      <div class="date-input-wrapper">
                        <input
                          type="date"
                          v-model="form.tanggalKejadianDate"
                          required
                          ref="tglInput"
                          @click="$refs.tglInput.showPicker()"
                        />
                        <svg
                          class="date-icon"
                          @click="$refs.tglInput.showPicker()"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          stroke-width="2"
                          width="17"
                          height="17"
                        >
                          <rect
                            x="3"
                            y="4"
                            width="18"
                            height="18"
                            rx="2"
                            ry="2"
                          />
                          <line x1="16" y1="2" x2="16" y2="6" />
                          <line x1="8" y1="2" x2="8" y2="6" />
                          <line x1="3" y1="10" x2="21" y2="10" />
                        </svg>
                      </div>
                    </div>
                  </div>

                  <div class="form-row">
                    <div class="form-group">
                      <label>Nama Korban <span class="required">*</span></label>
                      <div class="petugas-nama-wrap">
                        <input
                          type="text"
                          v-model="form.namaKorban"
                          @input="onKorbanInput"
                          @keydown="onKorbanKeydown"
                          @blur="onKorbanBlur"
                          required
                          placeholder="Nama korban atau ketik @ untuk cari..."
                          class="petugas-nama-input"
                          style="border-radius: 8px"
                        />
                        <div
                          v-if="
                            korbanMentionOpen && korbanMentionResults.length
                          "
                          class="mention-dropdown"
                        >
                          <button
                            v-for="(u, mi) in korbanMentionResults"
                            :key="u.id"
                            type="button"
                            :class="[
                              'mention-item',
                              {
                                'mention-item-active':
                                  korbanMentionHighlight === mi,
                              },
                            ]"
                            @mousedown.prevent="selectKorbanMention(u)"
                          >
                            <span class="mention-name">{{
                              u.fullName || u.username
                            }}</span>
                            <span v-if="u.departmentId" class="mention-dept">
                              {{
                                departments.find((d) => d.id === u.departmentId)
                                  ?.name || ''
                              }}
                            </span>
                          </button>
                        </div>
                      </div>
                    </div>
                    <div class="form-group">
                      <label>Dept. Korban</label>
                      <select v-model.number="form.korbanDeptId">
                        <option :value="null">-- Pilih Departemen --</option>
                        <option
                          v-for="d in departments"
                          :key="d.id"
                          :value="d.id"
                        >
                          {{ d.name }}
                        </option>
                      </select>
                    </div>
                  </div>

                  <div class="form-row">
                    <div class="form-group">
                      <label
                        >Status Karyawan <span class="required">*</span></label
                      >
                      <select v-model="form.statusKaryawan" required>
                        <option value="" disabled>-- Pilih Status --</option>
                        <option value="Karyawan">Karyawan</option>
                        <option value="OS/Borongan">OS/Borongan</option>
                        <option value="Kontraktor/Supplier">
                          Kontraktor/Supplier
                        </option>
                      </select>
                    </div>
                    <div class="form-group">
                      <label
                        >Jenis Kecelakaan <span class="required">*</span></label
                      >
                      <select v-model="form.jenisKecelakaan" required>
                        <option value="" disabled>-- Pilih Jenis --</option>
                        <option value="Near Miss">Near Miss</option>
                        <option value="P3K">P3K</option>
                        <option value="Medical Treatment">
                          Medical Treatment
                        </option>
                        <option value="LTI (Lost Time Injury)">
                          LTI (Lost Time Injury)
                        </option>
                        <option value="Fire">Fire</option>
                        <option value="Explosion">Explosion</option>
                        <option value="Konsleting Listrik">
                          Konsleting Listrik
                        </option>
                        <option value="Kerusakan Properti">
                          Kerusakan Properti
                        </option>
                        <option value="Kecelakaan Transportasi">
                          Kecelakaan Transportasi
                        </option>
                        <option value="Fatality">Fatality</option>
                        <option value="Pencemaran / Polusi Lingkungan">
                          Pencemaran / Polusi Lingkungan
                        </option>
                      </select>
                    </div>
                  </div>

                  <div class="form-row">
                    <div class="form-group form-group--full">
                      <label
                        >Lokasi Kecelakaan
                        <span class="required">*</span></label
                      >
                      <input
                        type="text"
                        v-model="form.lokasiKecelakaan"
                        required
                        placeholder="Lokasi kejadian insiden"
                      />
                    </div>
                  </div>
                </div>

                <!-- ── Foto Kejadian ── -->
                <div class="form-section">
                  <h4 class="section-title">
                    Foto Kejadian
                    <span class="photo-count-label"
                      >({{ photos.length }}/10)</span
                    >
                  </h4>
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
                          ×
                        </button>
                      </div>
                    </div>
                    <div class="photo-clear" v-if="photos.length > 1">
                      <button
                        type="button"
                        class="btn btn-clear"
                        @click="clearPhotos"
                      >
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
                          <rect
                            x="3"
                            y="3"
                            width="18"
                            height="18"
                            rx="2"
                            ry="2"
                          />
                          <circle cx="8.5" cy="8.5" r="1.5" />
                          <polyline points="21 15 16 10 5 21" />
                        </svg>
                        Galeri
                        <input
                          type="file"
                          accept="image/*"
                          multiple
                          @change="onPhotoSelect"
                          style="display: none"
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
                          style="display: none"
                        />
                      </label>
                    </div>
                  </div>
                </div>

                <!-- ── Hasil Investigasi ── -->
                <div class="form-section">
                  <h4 class="section-title">Hasil Investigasi</h4>
                  <div class="form-row">
                    <div class="form-group form-group--full">
                      <label>Deskripsi Kecelakaan</label>
                      <textarea
                        v-model="form.deskripsiKecelakaan"
                        rows="3"
                        placeholder="Uraikan kronologi dan detail kejadian..."
                      ></textarea>
                    </div>
                  </div>
                  <div class="form-row">
                    <div class="form-group form-group--full">
                      <label>Penyebab Kecelakaan</label>
                      <textarea
                        v-model="form.penyebabKecelakaan"
                        rows="3"
                        placeholder="Faktor penyebab langsung maupun tidak langsung..."
                      ></textarea>
                    </div>
                  </div>
                </div>

                <!-- ── Tindakan Perbaikan ── -->
                <div class="form-section">
                  <h4 class="section-title">Tindakan Perbaikan</h4>
                  <div class="form-row">
                    <div class="form-group form-group--full">
                      <label>Perbaikan yang Dilakukan</label>
                      <textarea
                        v-model="form.perbaikanDilakukan"
                        rows="3"
                        placeholder="Uraikan tindakan perbaikan yang telah atau akan dilakukan..."
                      ></textarea>
                    </div>
                  </div>
                  <div class="form-row">
                    <div class="form-group">
                      <label>Target Penyelesaian</label>
                      <div class="date-input-wrapper">
                        <input
                          type="date"
                          v-model="form.targetPenyelesaian"
                          ref="targetInput"
                          @click="$refs.targetInput.showPicker()"
                        />
                        <svg
                          class="date-icon"
                          @click="$refs.targetInput.showPicker()"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          stroke-width="2"
                          width="17"
                          height="17"
                        >
                          <rect
                            x="3"
                            y="4"
                            width="18"
                            height="18"
                            rx="2"
                            ry="2"
                          />
                          <line x1="16" y1="2" x2="16" y2="6" />
                          <line x1="8" y1="2" x2="8" y2="6" />
                          <line x1="3" y1="10" x2="21" y2="10" />
                        </svg>
                      </div>
                    </div>
                    <div class="form-group">
                      <label>Status</label>
                      <select v-model="form.status" :disabled="!canEditStatus">
                        <option value="Open">Open</option>
                        <option value="In Progress">In Progress</option>
                        <option value="Closed">Closed</option>
                      </select>
                    </div>
                  </div>
                </div>
              </form>
            </div>

            <div class="modal-footer-bar">
              <button type="button" class="btn-cancel" @click="tryClose">
                Batal
              </button>
              <button
                type="submit"
                form="ci-form"
                class="btn-primary"
                :disabled="submitting"
              >
                {{
                  submitting
                    ? 'Menyimpan...'
                    : editingId
                      ? 'Simpan Perubahan'
                      : 'Simpan Laporan'
                }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Update Confirm -->
    <Teleport to="body">
      <Transition name="modal">
        <div
          v-if="showUpdateConfirm"
          class="modal-overlay"
          style="z-index: 1100"
          @mousedown.self="showUpdateConfirm = false"
        >
          <div class="modal-container modal-sm">
            <div class="modal-header">
              <h3 class="modal-title">Simpan Perubahan?</h3>
              <button
                class="modal-close"
                type="button"
                @click="showUpdateConfirm = false"
              >
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  width="16"
                  height="16"
                >
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            </div>
            <div class="modal-body" style="padding: 16px 24px 20px">
              <p style="font-size: 14px; color: #475569; margin: 0">
                Perubahan pada laporan ini akan disimpan. Lanjutkan?
              </p>
            </div>
            <div class="modal-footer-bar">
              <button class="btn-cancel" @click="showUpdateConfirm = false">
                Batal
              </button>
              <button
                class="btn-primary"
                @click="doSaveCI"
                :disabled="submitting"
              >
                {{ submitting ? 'Menyimpan...' : 'Ya, Simpan' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Discard Confirm -->
    <Teleport to="body">
      <Transition name="modal">
        <div
          v-if="showDiscardConfirm"
          class="modal-overlay"
          style="z-index: 1100"
          @mousedown.self="showDiscardConfirm = false"
        >
          <div class="modal-container modal-sm">
            <div class="modal-body" style="padding: 28px 24px 20px">
              <div class="discard-icon">
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  width="36"
                  height="36"
                >
                  <path
                    d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"
                  />
                  <line x1="12" y1="9" x2="12" y2="13" />
                  <line x1="12" y1="17" x2="12.01" y2="17" />
                </svg>
              </div>
              <h4 class="discard-title">Batalkan perubahan?</h4>
              <p class="discard-desc">
                Anda memiliki data yang belum disimpan. Apakah yakin ingin
                menutup form ini?
              </p>
            </div>
            <div class="discard-footer">
              <button class="btn-cancel" @click="showDiscardConfirm = false">
                Kembali
              </button>
              <button class="btn btn-discard-confirm" @click="forceCloseCI">
                Ya, Batalkan
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- ── Detail Modal ── -->
    <Teleport to="body">
      <Transition name="modal">
        <div
          v-if="showViewModal && viewingRecord"
          class="modal-overlay"
          @click.self="closeViewModal"
        >
          <div class="modal-container modal-lg">
            <div class="modal-header">
              <h3 class="modal-title">Detail Laporan Insiden</h3>
              <button class="modal-close" type="button" @click="closeViewModal">
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  width="20"
                  height="20"
                >
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            </div>
            <div class="modal-body">
              <div class="detail-grid">
                <!-- Data Kecelakaan -->
                <div class="detail-section">
                  <h4 class="section-title">Data Kecelakaan</h4>
                  <div class="detail-row">
                    <span class="detail-label">Business Unit</span>
                    <span class="detail-value">{{
                      viewingRecord.businessUnitName ||
                      getBusinessUnitName(viewingRecord.businessUnitId)
                    }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">Plant</span>
                    <span class="detail-value">{{
                      viewingRecord.plantName ||
                      getPlantName(viewingRecord.plantId)
                    }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">Nama Pelapor</span>
                    <span class="detail-value">{{
                      viewingRecord.namaPelapor || '-'
                    }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">Dept. Pelapor</span>
                    <span class="detail-value">{{
                      departments.find(
                        (d) => d.id === viewingRecord.pelaporDeptId,
                      )?.name || '-'
                    }}</span>
                  </div>
                  <template v-if="parseSaksi(viewingRecord.saksiList).length">
                    <div
                      v-for="(s, i) in parseSaksi(viewingRecord.saksiList)"
                      :key="i"
                      class="detail-row"
                    >
                      <span class="detail-label">Saksi {{ i + 1 }}</span>
                      <span class="detail-value">
                        {{ s.nama }}
                        <span v-if="s.departmentId" class="petugas-dept-tag">{{
                          departments.find((d) => d.id === s.departmentId)
                            ?.name || ''
                        }}</span>
                      </span>
                    </div>
                  </template>
                  <div class="detail-row">
                    <span class="detail-label">Tanggal Kejadian</span>
                    <span class="detail-value">{{
                      formatDate(viewingRecord.tanggalKejadian)
                    }}</span>
                  </div>
                  <div class="detail-row" v-if="viewingRecord.tanggalPelaporan">
                    <span class="detail-label">Tanggal Pelaporan</span>
                    <span class="detail-value">{{
                      formatDate(viewingRecord.tanggalPelaporan)
                    }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">Nama Korban</span>
                    <span class="detail-value">{{
                      viewingRecord.namaKorban || '-'
                    }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">Dept. Korban</span>
                    <span class="detail-value">{{
                      departments.find(
                        (d) => d.id === viewingRecord.korbanDeptId,
                      )?.name || '-'
                    }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">Status Karyawan</span>
                    <span class="detail-value">{{
                      viewingRecord.statusKaryawan || '-'
                    }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">Jenis Kecelakaan</span>
                    <span class="detail-value">
                      <span
                        :class="[
                          'jenis-badge',
                          jenisClass(viewingRecord.jenisKecelakaan),
                        ]"
                        >{{ viewingRecord.jenisKecelakaan || '-' }}</span
                      >
                    </span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">Lokasi</span>
                    <span class="detail-value">{{
                      viewingRecord.lokasiKecelakaan || '-'
                    }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">Status</span>
                    <span class="detail-value">
                      <span
                        :class="[
                          'status-badge',
                          `status-${(viewingRecord.status || 'open').toLowerCase().replace(' ', '-')}`,
                        ]"
                        >{{ viewingRecord.status || 'Open' }}</span
                      >
                    </span>
                  </div>
                </div>

                <!-- Foto Kejadian -->
                <div
                  class="detail-section"
                  v-if="parsePhotos(viewingRecord.fotoKejadian).length"
                >
                  <h4 class="section-title">Foto Kejadian</h4>
                  <div class="detail-photo-grid">
                    <img
                      v-for="(url, idx) in parsePhotos(
                        viewingRecord.fotoKejadian,
                      )"
                      :key="idx"
                      :src="url"
                      alt="Foto kejadian"
                      class="detail-photo-thumb"
                      @click="
                        openPhotoModalFromUrls(
                          parsePhotos(viewingRecord.fotoKejadian),
                          idx,
                        )
                      "
                    />
                  </div>
                </div>

                <!-- Hasil Investigasi -->
                <div
                  class="detail-section"
                  v-if="
                    viewingRecord.deskripsiKecelakaan ||
                    viewingRecord.penyebabKecelakaan
                  "
                >
                  <h4 class="section-title">Hasil Investigasi</h4>
                  <div
                    class="detail-row"
                    v-if="viewingRecord.deskripsiKecelakaan"
                  >
                    <span class="detail-label">Deskripsi</span>
                    <span class="detail-value detail-multiline">{{
                      viewingRecord.deskripsiKecelakaan
                    }}</span>
                  </div>
                  <div
                    class="detail-row"
                    v-if="viewingRecord.penyebabKecelakaan"
                  >
                    <span class="detail-label">Penyebab</span>
                    <span class="detail-value detail-multiline">{{
                      viewingRecord.penyebabKecelakaan
                    }}</span>
                  </div>
                </div>

                <!-- Tindakan Perbaikan -->
                <div
                  class="detail-section"
                  v-if="
                    viewingRecord.perbaikanDilakukan ||
                    viewingRecord.targetPenyelesaian
                  "
                >
                  <h4 class="section-title">Tindakan Perbaikan</h4>
                  <div
                    class="detail-row"
                    v-if="viewingRecord.perbaikanDilakukan"
                  >
                    <span class="detail-label">Perbaikan Dilakukan</span>
                    <span class="detail-value detail-multiline">{{
                      viewingRecord.perbaikanDilakukan
                    }}</span>
                  </div>
                  <div
                    class="detail-row"
                    v-if="viewingRecord.targetPenyelesaian"
                  >
                    <span class="detail-label">Target Penyelesaian</span>
                    <span class="detail-value">{{
                      viewingRecord.targetPenyelesaian
                    }}</span>
                  </div>
                </div>
              </div>
            </div>
            <div class="modal-footer-bar">
              <button type="button" class="btn-cancel" @click="closeViewModal">
                Tutup
              </button>
              <button
                type="button"
                class="btn-primary"
                @click="openEditFromDetail"
              >
                Ubah
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- ── Lightbox ── -->
    <Teleport to="body">
      <Transition name="lightbox-fade">
        <div
          v-if="showPhotoModal"
          class="lightbox-overlay"
          @click.self="showPhotoModal = false"
          @keydown.left="
            photoModalIndex =
              (photoModalIndex - 1 + photoModalImages.length) %
              photoModalImages.length
          "
          @keydown.right="
            photoModalIndex = (photoModalIndex + 1) % photoModalImages.length
          "
          @keydown.esc="showPhotoModal = false"
          tabindex="0"
        >
          <button class="lightbox-close" @click="showPhotoModal = false">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              width="24"
              height="24"
            >
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
          <button
            class="lightbox-download"
            @click="downloadCurrentPhoto"
            title="Download foto"
          >
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              width="22"
              height="22"
            >
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="7 10 12 15 17 10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>
          </button>
          <button
            class="lightbox-nav lightbox-prev"
            v-if="photoModalImages.length > 1"
            @click="
              photoModalIndex =
                (photoModalIndex - 1 + photoModalImages.length) %
                photoModalImages.length
            "
          >
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2.5"
              width="22"
              height="22"
            >
              <polyline points="15 18 9 12 15 6" />
            </svg>
          </button>
          <div class="lightbox-content">
            <img
              :src="photoModalImages[photoModalIndex]"
              alt="Foto"
              class="lightbox-img"
            />
          </div>
          <div v-if="photoModalImages.length > 1" class="lightbox-dots">
            <span
              v-for="(_, i) in photoModalImages"
              :key="i"
              class="lightbox-dot"
              :class="{ active: i === photoModalIndex }"
              @click.stop="photoModalIndex = i"
            ></span>
          </div>
          <button
            class="lightbox-nav lightbox-next"
            v-if="photoModalImages.length > 1"
            @click="
              photoModalIndex = (photoModalIndex + 1) % photoModalImages.length
            "
          >
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2.5"
              width="22"
              height="22"
            >
              <polyline points="9 18 15 12 9 6" />
            </svg>
          </button>
        </div>
      </Transition>
    </Teleport>

    <!-- ── Delete Confirm Modal ── -->
    <Teleport to="body">
      <Transition name="modal">
        <div
          v-if="showDeleteModal"
          class="modal-overlay"
          @click.self="showDeleteModal = false"
        >
          <div class="modal-container modal-sm">
            <div class="modal-header modal-header-danger">
              <div class="modal-title-group">
                <div class="modal-danger-icon">
                  <svg
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    width="22"
                    height="22"
                  >
                    <polyline points="3 6 5 6 21 6" />
                    <path
                      d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"
                    />
                  </svg>
                </div>
                <h3 class="modal-title">Hapus Laporan</h3>
              </div>
              <button class="modal-close" @click="showDeleteModal = false">
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  width="20"
                  height="20"
                >
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            </div>
            <div class="modal-body delete-modal-body">
              <p class="delete-msg">
                Apakah Anda yakin ingin menghapus laporan insiden ini? Tindakan
                ini tidak dapat dibatalkan.
              </p>
              <div v-if="deletingRecord" class="delete-preview">
                <div class="delete-preview-row">
                  <span class="delete-preview-label">Nama Korban</span>
                  <span>{{ deletingRecord.namaKorban || '-' }}</span>
                </div>
                <div class="delete-preview-row">
                  <span class="delete-preview-label">Jenis</span>
                  <span
                    :class="[
                      'jenis-badge',
                      jenisClass(deletingRecord.jenisKecelakaan),
                    ]"
                    >{{ deletingRecord.jenisKecelakaan || '-' }}</span
                  >
                </div>
                <div
                  class="delete-preview-row"
                  v-if="deletingRecord.lokasiKecelakaan"
                >
                  <span class="delete-preview-label">Lokasi</span>
                  <span class="delete-preview-desc">{{
                    deletingRecord.lokasiKecelakaan
                  }}</span>
                </div>
              </div>
              <div class="delete-actions">
                <button
                  class="btn btn-delete-confirm"
                  :disabled="deleting"
                  @click="confirmDelete"
                >
                  <svg
                    v-if="!deleting"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    width="15"
                    height="15"
                  >
                    <polyline points="3 6 5 6 21 6" />
                    <path
                      d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"
                    />
                  </svg>
                  {{ deleting ? 'Menghapus...' : 'Ya, Hapus' }}
                </button>
                <button
                  class="btn-secondary"
                  @click="showDeleteModal = false"
                  :disabled="deleting"
                >
                  Batal
                </button>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- ── Toast notification ── -->
    <Teleport to="body">
      <Transition name="toast">
        <div v-if="toast.show" :class="['toast', `toast-${toast.type}`]">
          <span class="toast-text">{{ toast.message }}</span>
          <button class="toast-close" @click="toast.show = false">x</button>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue';
import { authService } from '@/services/authService.js';
import { inspectionK3LService } from '@/services/inspectionK3LService.js';
import { uploadImage } from '@/services/inspectionK3LService.js';
import { caseIncidentService } from '@/services/caseIncidentService.js';
import { usePagination } from '@/composables/usePagination.js';
import { exportToCsv } from '@/services/exportCsvService.js';
import PaginationBar from '@/components/PaginationBar.vue';

const currentUser = authService.getCurrentUser();
const roleLevel = authService.getRoleLevel();
const isPrivileged = roleLevel <= 3;
const canEditStatus = isPrivileged || currentUser?.department === 'Safety';

// ── Toast ──
const toast = reactive({ show: false, message: '', type: 'success' });
let toastTimer = null;

function showToast(msg, type = 'success') {
  if (toastTimer) clearTimeout(toastTimer);
  toast.show = true;
  toast.message = msg;
  toast.type = type;
  toastTimer = setTimeout(() => {
    toast.show = false;
  }, 4000);
}

// ── Table state ──
const records = ref([]);
const loading = ref(false);

async function loadRecords() {
  loading.value = true;
  try {
    records.value = await caseIncidentService.list();
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
}

// ── Search / filter ──
const searchQuery = ref('');
const filterJenis = ref('');
const filterStatus = ref('');
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
  if (val !== 'custom') {
    customDateFrom.value = '';
    customDateTo.value = '';
  }
}

function matchesDateFilter(item) {
  if (filterDate.value === 'all') return true;
  if (!item.tanggalKejadian) return false;
  const d = new Date(String(item.tanggalKejadian).replace(' ', 'T'));
  if (isNaN(d)) return false;
  d.setHours(0, 0, 0, 0);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  if (filterDate.value === 'today') return d.getTime() === today.getTime();
  if (filterDate.value === 'week') {
    const start = new Date(today);
    start.setDate(today.getDate() - today.getDay());
    const end = new Date(start);
    end.setDate(start.getDate() + 6);
    return d >= start && d <= end;
  }
  if (filterDate.value === 'month') {
    return d.getMonth() === today.getMonth() && d.getFullYear() === today.getFullYear();
  }
  if (filterDate.value === 'custom') {
    if (customDateFrom.value) {
      const from = new Date(customDateFrom.value);
      from.setHours(0, 0, 0, 0);
      if (d < from) return false;
    }
    if (customDateTo.value) {
      const to = new Date(customDateTo.value);
      to.setHours(0, 0, 0, 0);
      if (d > to) return false;
    }
  }
  return true;
}

const hasActiveFilters = computed(
  () =>
    searchQuery.value.trim() !== '' ||
    filterJenis.value !== '' ||
    filterStatus.value !== '' ||
    filterDate.value !== 'all',
);

const filteredRecords = computed(() => {
  let result = records.value;
  if (filterJenis.value)
    result = result.filter((r) => r.jenisKecelakaan === filterJenis.value);
  if (filterStatus.value)
    result = result.filter((r) => r.status === filterStatus.value);
  if (filterDate.value !== 'all') result = result.filter(matchesDateFilter);
  const q = searchQuery.value.trim().toLowerCase();
  if (q) {
    result = result.filter(
      (r) =>
        (r.namaKorban || '').toLowerCase().includes(q) ||
        (r.namaPelapor || '').toLowerCase().includes(q) ||
        (r.lokasiKecelakaan || '').toLowerCase().includes(q) ||
        (r.jenisKecelakaan || '').toLowerCase().includes(q) ||
        (r.statusKaryawan || '').toLowerCase().includes(q) ||
        (r.status || '').toLowerCase().includes(q),
    );
  }
  return result;
});

function resetFilters() {
  searchQuery.value = '';
  filterJenis.value = '';
  filterStatus.value = '';
  filterDate.value = 'all';
  customDateFrom.value = '';
  customDateTo.value = '';
}

// ── Excel export ──
function buildCiExport(source) {
  const parsedFotos = source.map(r => parsePhotos(r.fotoKejadian));
  const maxFotos = Math.max(parsedFotos.reduce((m, p) => Math.max(m, p.length), 0), 1);
  const fotoCols = Array.from({ length: maxFotos }, (_, i) => ({
    label: maxFotos === 1 ? 'Foto Kejadian' : `Foto Kejadian ${i + 1}`,
    key: `foto_${i}`,
    image: true,
  }));
  const deptName = (id) => departments.value.find(d => d.id === id)?.name || '';

  const columns = [
    { label: 'No', key: 'no' },
    { label: 'Tanggal Kejadian', key: 'tanggalKejadian' },
    { label: 'Tanggal Pelaporan', key: 'tanggalPelaporan' },
    { label: 'Business Unit', key: 'businessUnit' },
    { label: 'Plant', key: 'plant' },
    { label: 'Nama Pelapor', key: 'namaPelapor' },
    { label: 'Nama Korban', key: 'namaKorban' },
    { label: 'Dept. Korban', key: 'deptKorban' },
    { label: 'Status Karyawan', key: 'statusKaryawan' },
    { label: 'Jenis Kecelakaan', key: 'jenisKecelakaan' },
    { label: 'Lokasi', key: 'lokasi' },
    { label: 'Deskripsi Kecelakaan', key: 'deskripsi' },
    { label: 'Penyebab Kecelakaan', key: 'penyebab' },
    { label: 'Perbaikan Dilakukan', key: 'perbaikan' },
    { label: 'Target Penyelesaian', key: 'target' },
    { label: 'Status', key: 'status' },
    ...fotoCols,
  ];

  const rows = source.map((r, idx) => {
    const fotos = parsedFotos[idx];
    const fotoFields = {};
    for (let i = 0; i < maxFotos; i++) fotoFields[`foto_${i}`] = fotos[i] || '';
    return {
      no: idx + 1,
      tanggalKejadian: r.tanggalKejadian ? formatDate(r.tanggalKejadian) : '',
      tanggalPelaporan: r.tanggalPelaporan ? formatDate(r.tanggalPelaporan) : '',
      businessUnit: r.businessUnitName || getBusinessUnitName(r.businessUnitId),
      plant: r.plantName || getPlantName(r.plantId),
      namaPelapor: r.namaPelapor || '',
      namaKorban: r.namaKorban || '',
      deptKorban: deptName(r.korbanDeptId),
      statusKaryawan: r.statusKaryawan || '',
      jenisKecelakaan: r.jenisKecelakaan || '',
      lokasi: r.lokasiKecelakaan || '',
      deskripsi: r.deskripsiKecelakaan || '',
      penyebab: r.penyebabKecelakaan || '',
      perbaikan: r.perbaikanDilakukan || '',
      target: r.targetPenyelesaian || '',
      status: r.status || 'Open',
      ...fotoFields,
    };
  });

  return { columns, rows };
}

async function exportExcel() {
  if (!filteredRecords.value.length) return;
  const { columns, rows } = buildCiExport(filteredRecords.value);
  const today = new Date().toISOString().slice(0, 10);
  await exportToCsv(`case-incident-${today}.xlsx`, columns, rows);
}

// ── Pagination ──
const {
  currentPage: ciCurrentPage,
  perPage: ciPerPage,
  totalItems: ciTotalItems,
  totalPages: ciTotalPages,
  paginatedItems: pagedRecords,
  goToPage: ciGoToPage,
  setPerPage: ciSetPerPage,
} = usePagination(filteredRecords);

// ── Helpers ──
function formatDate(val) {
  if (!val) return '-';
  const d = new Date(val.replace(' ', 'T'));
  if (isNaN(d)) return val;
  const dd = String(d.getDate()).padStart(2, '0');
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const yyyy = d.getFullYear();
  const hh = String(d.getHours()).padStart(2, '0');
  const min = String(d.getMinutes()).padStart(2, '0');
  return `${dd}/${mm}/${yyyy} ${hh}:${min}`;
}

function parsePhotos(val) {
  if (!val) return [];
  try {
    return JSON.parse(val);
  } catch {
    return [];
  }
}

const JENIS_DANGER = [
  'Fatality',
  'LTI (Lost Time Injury)',
  'Fire',
  'Explosion',
];
const JENIS_WARNING = [
  'Medical Treatment',
  'Pencemaran / Polusi Lingkungan',
  'Kecelakaan Transportasi',
  'Konsleting Listrik',
  'Kerusakan Properti',
];
function jenisClass(j) {
  if (!j) return '';
  if (JENIS_DANGER.includes(j)) return 'jenis-danger';
  if (JENIS_WARNING.includes(j)) return 'jenis-warning';
  return 'jenis-default';
}

// ── Form modal ──
const showForm = ref(false);
const editingId = ref(null);
const submitting = ref(false);
const showUpdateConfirm = ref(false);
const showDiscardConfirm = ref(false);
const originalForm = ref(null);
const departments = ref([]);
const usersForMention = ref([]);
const businessUnits = ref([]);
const plants = ref([]);

function getBusinessUnitName(id) {
  if (!id) return '-';
  return businessUnits.value.find((u) => u.id === id)?.name ?? '-';
}

function getPlantName(id) {
  if (!id) return '-';
  return plants.value.find((p) => p.id === id)?.name ?? '-';
}

// ── Saksi mention ──
const saksiList = ref([{ nama: '', departmentId: null }]);
const saksiMentionActive = ref(-1);
const saksiMentionQuery = ref('');
const saksiMentionHighlight = ref(-1);

const saksiMentionResults = computed(() => {
  if (!saksiMentionQuery.value) return [];
  const q = saksiMentionQuery.value.toLowerCase();
  return usersForMention.value
    .filter(
      (u) =>
        (u.fullName || '').toLowerCase().includes(q) ||
        (u.username || '').toLowerCase().includes(q),
    )
    .slice(0, 8);
});

function onSaksiInput(idx, e) {
  const val = e.target.value;
  const atPos = val.lastIndexOf('@');
  if (atPos !== -1) {
    saksiMentionActive.value = idx;
    saksiMentionQuery.value = val.slice(atPos + 1);
    saksiMentionHighlight.value = 0;
  } else {
    if (saksiMentionActive.value === idx) {
      saksiMentionActive.value = -1;
      saksiMentionQuery.value = '';
      saksiMentionHighlight.value = -1;
    }
  }
}

function onSaksiKeydown(idx, e) {
  if (saksiMentionActive.value !== idx || !saksiMentionResults.value.length)
    return;
  if (e.key === 'ArrowDown') {
    e.preventDefault();
    saksiMentionHighlight.value =
      (saksiMentionHighlight.value + 1) % saksiMentionResults.value.length;
  } else if (e.key === 'ArrowUp') {
    e.preventDefault();
    saksiMentionHighlight.value =
      (saksiMentionHighlight.value - 1 + saksiMentionResults.value.length) %
      saksiMentionResults.value.length;
  } else if (e.key === 'Enter') {
    e.preventDefault();
    const u = saksiMentionResults.value[saksiMentionHighlight.value];
    if (u) selectSaksiMention(idx, u);
  } else if (e.key === 'Escape') {
    saksiMentionActive.value = -1;
    saksiMentionQuery.value = '';
    saksiMentionHighlight.value = -1;
  }
}

function selectSaksiMention(idx, user) {
  saksiList.value[idx].nama = user.fullName || user.username || '';
  saksiList.value[idx].departmentId = user.departmentId || null;
  saksiMentionActive.value = -1;
  saksiMentionQuery.value = '';
  saksiMentionHighlight.value = -1;
}

function addSaksi() {
  saksiList.value.push({ nama: '', departmentId: null });
}
function removeSaksi(idx) {
  if (saksiList.value.length > 1) saksiList.value.splice(idx, 1);
}
function onSaksiBlur(idx) {
  setTimeout(() => {
    if (saksiMentionActive.value === idx) {
      saksiMentionActive.value = -1;
      saksiMentionQuery.value = '';
    }
  }, 150);
}

// ── Korban mention ──
const korbanMentionOpen = ref(false);
const korbanMentionQuery = ref('');
const korbanMentionHighlight = ref(0);

const korbanMentionResults = computed(() => {
  if (!korbanMentionQuery.value) return [];
  const q = korbanMentionQuery.value.toLowerCase();
  return usersForMention.value
    .filter(
      (u) =>
        (u.fullName || '').toLowerCase().includes(q) ||
        (u.username || '').toLowerCase().includes(q),
    )
    .slice(0, 8);
});

function onKorbanInput(e) {
  const val = e.target.value;
  const atPos = val.lastIndexOf('@');
  if (atPos !== -1) {
    korbanMentionOpen.value = true;
    korbanMentionQuery.value = val.slice(atPos + 1);
    korbanMentionHighlight.value = 0;
  } else {
    korbanMentionOpen.value = false;
    korbanMentionQuery.value = '';
  }
}

function onKorbanKeydown(e) {
  if (!korbanMentionOpen.value || !korbanMentionResults.value.length) return;
  if (e.key === 'ArrowDown') {
    e.preventDefault();
    korbanMentionHighlight.value =
      (korbanMentionHighlight.value + 1) % korbanMentionResults.value.length;
  } else if (e.key === 'ArrowUp') {
    e.preventDefault();
    korbanMentionHighlight.value =
      (korbanMentionHighlight.value - 1 + korbanMentionResults.value.length) %
      korbanMentionResults.value.length;
  } else if (e.key === 'Enter') {
    e.preventDefault();
    const u = korbanMentionResults.value[korbanMentionHighlight.value];
    if (u) selectKorbanMention(u);
  } else if (e.key === 'Escape') {
    korbanMentionOpen.value = false;
  }
}

function selectKorbanMention(user) {
  form.value.namaKorban = user.fullName || user.username || '';
  form.value.korbanDeptId = user.departmentId || null;
  korbanMentionOpen.value = false;
  korbanMentionQuery.value = '';
}

function onKorbanBlur() {
  setTimeout(() => {
    korbanMentionOpen.value = false;
    korbanMentionQuery.value = '';
  }, 150);
}

// ── Photos ──
const photos = ref([]);

function onPhotoSelect(event) {
  const files = Array.from(event.target.files);
  if (!files.length) return;
  const remaining = 10 - photos.value.length;
  if (files.length > remaining) {
    event.target.value = '';
    showToast(
      `Maksimal 10 foto. Anda hanya dapat menambahkan ${remaining} foto lagi.`,
      'warning',
    );
    return;
  }
  for (const file of files) {
    photos.value.push({ file, preview: URL.createObjectURL(file) });
  }
  event.target.value = '';
}

function removePhotoAt(idx) {
  const photo = photos.value[idx];
  if (photo.preview?.startsWith('blob:')) URL.revokeObjectURL(photo.preview);
  photos.value.splice(idx, 1);
}

function clearPhotos() {
  photos.value.forEach((p) => {
    if (p.preview?.startsWith('blob:')) URL.revokeObjectURL(p.preview);
  });
  photos.value = [];
}

async function uploadPhotoList(photoList) {
  if (!photoList.length) return null;
  const urls = [];
  for (const photo of photoList) {
    if (photo.file) urls.push(await uploadImage(photo.file));
    else if (photo.preview) urls.push(photo.preview);
  }
  return JSON.stringify(urls);
}

// ── Form ──
const emptyForm = () => ({
  businessUnitId: currentUser?.businessUnitId ?? null,
  plantId: currentUser?.plantId ?? null,
  tanggalKejadianDate: '',
  namaKorban: '',
  korbanDeptId: null,
  statusKaryawan: '',
  jenisKecelakaan: '',
  lokasiKecelakaan: '',
  deskripsiKecelakaan: '',
  penyebabKecelakaan: '',
  perbaikanDilakukan: '',
  targetPenyelesaian: '',
  status: 'Open',
});

const form = ref(emptyForm());

function nowWIB() {
  const now = new Date();
  const wib = new Date(now.getTime() + 7 * 60 * 60 * 1000);
  return wib.toISOString().slice(0, 16);
}

function currentTimeWIB() {
  const now = new Date();
  const wib = new Date(now.getTime() + 7 * 60 * 60 * 1000);
  return wib.toISOString().slice(11, 16);
}

function openForm() {
  editingId.value = null;
  form.value = emptyForm();
  originalForm.value = null;
  saksiList.value = [{ nama: '', departmentId: null }];
  photos.value = [];
  showForm.value = true;
}

function editRecord(item) {
  editingId.value = item.id;
  try {
    const parsed = JSON.parse(item.saksiList || '[]');
    saksiList.value = parsed.length
      ? parsed
      : [{ nama: '', departmentId: null }];
  } catch {
    saksiList.value = [{ nama: '', departmentId: null }];
  }
  try {
    const urls = JSON.parse(item.fotoKejadian || '[]');
    photos.value = urls.map((url) => ({ file: null, preview: url }));
  } catch {
    photos.value = [];
  }
  form.value = {
    businessUnitId: currentUser?.businessUnitId ?? null,
    plantId: currentUser?.plantId ?? null,
    tanggalKejadianDate: item.tanggalKejadian
      ? item.tanggalKejadian.slice(0, 10)
      : '',
    namaKorban: item.namaKorban || '',
    korbanDeptId: item.korbanDeptId || null,
    statusKaryawan: item.statusKaryawan || '',
    jenisKecelakaan: item.jenisKecelakaan || '',
    lokasiKecelakaan: item.lokasiKecelakaan || '',
    deskripsiKecelakaan: item.deskripsiKecelakaan || '',
    penyebabKecelakaan: item.penyebabKecelakaan || '',
    perbaikanDilakukan: item.perbaikanDilakukan || '',
    targetPenyelesaian: item.targetPenyelesaian || '',
    status: item.status || 'Open',
  };
  originalForm.value = {
    ...form.value,
    saksiCount: saksiList.value.length,
    photoCount: photos.value.length,
  };
  showForm.value = true;
}

// ── Delete confirm ──
const showDeleteModal = ref(false);
const deletingRecord = ref(null);
const deleting = ref(false);

function deleteRecord(item) {
  deletingRecord.value = item;
  showDeleteModal.value = true;
}

async function confirmDelete() {
  if (!deletingRecord.value) return;
  deleting.value = true;
  try {
    await caseIncidentService.delete(deletingRecord.value.id);
    showToast('Laporan berhasil dihapus');
    showDeleteModal.value = false;
    deletingRecord.value = null;
    await loadRecords();
  } catch (e) {
    showToast(e.message, 'error');
  } finally {
    deleting.value = false;
  }
}

function hasFormChanges() {
  const f = form.value;
  if (!editingId.value) {
    return !!(
      f.tanggalKejadianDate ||
      f.namaKorban ||
      f.statusKaryawan ||
      f.jenisKecelakaan ||
      f.lokasiKecelakaan ||
      f.deskripsiKecelakaan ||
      f.penyebabKecelakaan ||
      f.perbaikanDilakukan ||
      f.targetPenyelesaian ||
      saksiList.value.some((s) => s.nama.trim()) ||
      photos.value.length > 0
    );
  }
  if (!originalForm.value) return false;
  const o = originalForm.value;
  return (
    f.tanggalKejadianDate !== o.tanggalKejadianDate ||
    f.namaKorban !== o.namaKorban ||
    f.korbanDeptId !== o.korbanDeptId ||
    f.statusKaryawan !== o.statusKaryawan ||
    f.jenisKecelakaan !== o.jenisKecelakaan ||
    f.lokasiKecelakaan !== o.lokasiKecelakaan ||
    f.deskripsiKecelakaan !== o.deskripsiKecelakaan ||
    f.penyebabKecelakaan !== o.penyebabKecelakaan ||
    f.perbaikanDilakukan !== o.perbaikanDilakukan ||
    f.targetPenyelesaian !== o.targetPenyelesaian ||
    f.status !== o.status ||
    saksiList.value.length !== o.saksiCount ||
    photos.value.some((p) => p.file !== null) ||
    photos.value.length !== o.photoCount
  );
}

function tryClose() {
  if (submitting.value) return;
  if (hasFormChanges()) {
    showDiscardConfirm.value = true;
    return;
  }
  forceCloseCI();
}

function forceCloseCI() {
  showDiscardConfirm.value = false;
  showForm.value = false;
  editingId.value = null;
  originalForm.value = null;
  form.value = emptyForm();
  saksiList.value = [{ nama: '', departmentId: null }];
  clearPhotos();
}

async function submitForm() {
  if (editingId.value) {
    showUpdateConfirm.value = true;
    return;
  }
  await doSaveCI();
}

async function doSaveCI() {
  submitting.value = true;
  try {
    const tanggalKejadian = form.value.tanggalKejadianDate
      ? `${form.value.tanggalKejadianDate}T${currentTimeWIB()}`
      : '';
    const tanggalPelaporan = nowWIB();
    const namaPelapor = currentUser?.fullName || currentUser?.username || '';
    const pelaporDeptId = currentUser?.departmentId || null;
    const saksiListJson =
      JSON.stringify(
        saksiList.value
          .filter((s) => s.nama.trim())
          .map((s) => ({ nama: s.nama.trim(), departmentId: s.departmentId })),
      ) || null;
    const fotoKejadianJson = await uploadPhotoList(photos.value);

    const payload = {
      namaPelapor,
      pelaporDeptId,
      saksiList: saksiListJson,
      tanggalKejadian,
      tanggalPelaporan,
      namaKorban: form.value.namaKorban,
      korbanDeptId: form.value.korbanDeptId,
      statusKaryawan: form.value.statusKaryawan,
      jenisKecelakaan: form.value.jenisKecelakaan,
      lokasiKecelakaan: form.value.lokasiKecelakaan,
      deskripsiKecelakaan: form.value.deskripsiKecelakaan || null,
      penyebabKecelakaan: form.value.penyebabKecelakaan || null,
      perbaikanDilakukan: form.value.perbaikanDilakukan || null,
      fotoKejadian: fotoKejadianJson,
      targetPenyelesaian: form.value.targetPenyelesaian || null,
      status: form.value.status,
      businessUnitId: form.value.businessUnitId,
      plantId: form.value.plantId,
    };

    if (editingId.value) {
      await caseIncidentService.update(editingId.value, payload);
      showToast('Laporan berhasil diperbarui');
    } else {
      await caseIncidentService.create(payload);
      showToast('Laporan berhasil disimpan');
    }
    showUpdateConfirm.value = false;
    forceCloseCI();
    await loadRecords();
  } catch (e) {
    showToast(e.message, 'error');
    showUpdateConfirm.value = false;
  } finally {
    submitting.value = false;
  }
}

// ── View detail ──
const showViewModal = ref(false);
const viewingRecord = ref(null);

function viewRecord(item) {
  viewingRecord.value = item;
  showViewModal.value = true;
}

function closeViewModal() {
  showViewModal.value = false;
  viewingRecord.value = null;
}

function openEditFromDetail() {
  const r = viewingRecord.value;
  closeViewModal();
  editRecord(r);
}

function parseSaksi(val) {
  if (!val) return [];
  try {
    return JSON.parse(val);
  } catch {
    return [];
  }
}

// ── Lightbox ──
const showPhotoModal = ref(false);
const photoModalImages = ref([]);
const photoModalIndex = ref(0);

function openPhotoModalFromUrls(urls, idx) {
  photoModalImages.value = urls;
  photoModalIndex.value = idx;
  showPhotoModal.value = true;
  nextTick(() => document.querySelector('.lightbox-overlay')?.focus());
}

async function downloadCurrentPhoto() {
  const url = photoModalImages.value[photoModalIndex.value];
  if (!url) return;
  try {
    const res = await fetch(url);
    const blob = await res.blob();
    const ext = url.split('.').pop()?.split('?')[0] || 'jpg';
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `foto_kejadian_${Date.now()}.${ext}`;
    a.click();
    URL.revokeObjectURL(a.href);
  } catch {
    window.open(url, '_blank');
  }
}

onMounted(async () => {
  const [depts, users, units, plantOptions] = await Promise.all([
    inspectionK3LService.listDepartments().catch(() => []),
    inspectionK3LService.listUsers().catch(() => []),
    inspectionK3LService.listBusinessUnits().catch(() => []),
    inspectionK3LService.listPlants().catch(() => []),
  ]);
  departments.value = depts;
  usersForMention.value = users;
  businessUnits.value = units;
  plants.value = plantOptions;
  await loadRecords();
});
</script>

<style scoped>
/* ── Page layout ── */
.case-incident {
  padding: 28px 32px;
  max-width: 1400px;
  overflow-x: hidden;
}
@media (max-width: 1024px) {
  .case-incident {
    padding: 20px;
  }
}
@media (max-width: 640px) {
  .case-incident {
    padding: 16px 14px;
  }
}

/* ── Page header ── */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
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
@media (max-width: 640px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .btn-primary {
    width: 100%;
    justify-content: center;
  }
}

/* ── Buttons ── */
.btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 9px 18px;
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
  white-space: nowrap;
}
.btn-primary:hover {
  background: #1d4ed8;
}
.btn-primary:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.btn-cancel {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 9px 18px;
  background: #f1f5f9;
  color: #475569;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-cancel:hover {
  background: #e2e8f0;
}

/* ── Filter bar ── */
.filter-bar {
  display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
  padding: 12px 20px; border-bottom: 1px solid #f1f5f9;
}
/* Data header export button */
.btn-export {
  display: inline-flex; align-items: center; gap: 5px;
  background: #f0fdf4; color: #166534; border: 1px solid #bbf7d0;
  border-radius: 6px; padding: 7px 12px; font-size: 13px; font-weight: 500;
  cursor: pointer; white-space: nowrap; transition: background 0.15s;
}
.btn-export:hover:not(:disabled) { background: #dcfce7; border-color: #86efac; }
.btn-export:disabled { opacity: 0.5; cursor: not-allowed; }
/* Date filter chips */
.date-chip {
  background: #f1f5f9; border: 1px solid transparent; border-radius: 20px;
  padding: 5px 14px; font-size: 13px; color: #64748b; cursor: pointer;
  transition: all 0.15s; white-space: nowrap; flex-shrink: 0;
}
.date-chip:hover { background: #e2e8f0; color: #1e293b; }
.date-chip.active { background: #3b82f6; color: #fff; border-color: #3b82f6; }
.custom-date-row {
  display: flex; align-items: center; gap: 8px;
  padding: 0 20px 10px; flex-wrap: wrap; border-bottom: 1px solid #f1f5f9;
}
.toolbar-date-wrap {
  display: inline-flex; border: 1px solid #cbd5e1; border-radius: 8px;
  background: #fff; overflow: hidden; cursor: pointer; transition: border-color 0.15s;
}
.toolbar-date-wrap:focus-within { border-color: #3b82f6; }
.toolbar-date {
  border: none; background: transparent; color: #1e293b; font-size: 13px;
  padding: 6px 10px; outline: none; cursor: pointer; color-scheme: light; width: 140px;
}
.date-sep { color: #94a3b8; font-size: 13px; }
.search-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 200px;
}
.search-icon {
  position: absolute;
  left: 10px;
  color: #94a3b8;
  pointer-events: none;
}
.search-input {
  width: 100%;
  padding: 8px 32px 8px 32px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  color: #1e293b;
  background: #fff;
  outline: none;
  transition: border-color 0.15s;
}
.search-input:focus {
  border-color: #3b82f6;
}
.search-clear {
  position: absolute;
  right: 8px;
  background: none;
  border: none;
  cursor: pointer;
  color: #94a3b8;
  font-size: 16px;
  line-height: 1;
  padding: 2px 4px;
}
.search-clear:hover {
  color: #475569;
}
.filter-select {
  padding: 8px 10px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 13px;
  color: #374151;
  background: #fff;
  cursor: pointer;
  outline: none;
  min-width: 140px;
}
.filter-select:focus {
  border-color: #3b82f6;
}
.btn-reset-filters {
  padding: 8px 14px;
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}
.btn-reset-filters:hover {
  background: #fee2e2;
}
.filter-count {
  font-size: 13px;
  color: #64748b;
  white-space: nowrap;
}

/* ── Table ── */
.table-wrapper {
  overflow-x: auto;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  background: #fff;
}

/* ── Mobile card list ── */
.card-list { display: none; }
.row-card {
  border: 1px solid #e2e8f0; border-radius: 12px; background: #fff;
  padding: 12px 14px; display: flex; flex-direction: column; gap: 10px;
  cursor: pointer; transition: box-shadow 0.15s;
}
.row-card:active { box-shadow: 0 2px 10px rgba(0,0,0,0.08); }
.rc-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 10px; }
.rc-title { font-size: 14px; font-weight: 700; color: #1e293b; line-height: 1.3; }
.rc-sub { font-size: 12px; color: #64748b; margin-top: 2px; }
.rc-body { display: flex; flex-direction: column; gap: 6px; }
.rc-row { display: flex; justify-content: space-between; gap: 12px; font-size: 13px; }
.rc-label { color: #64748b; flex-shrink: 0; }
.rc-value { color: #1e293b; text-align: right; word-break: break-word; }
.rc-footer {
  display: flex; align-items: center; justify-content: space-between; gap: 10px;
  padding-top: 10px; border-top: 1px solid #f1f5f9;
}
.rc-actions { display: flex; gap: 6px; }
@media (max-width: 768px) {
  .table-wrapper table { display: none; }
  .card-list { display: flex; flex-direction: column; gap: 12px; padding: 12px; }
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 900px;
}
thead tr {
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}
thead th {
  padding: 11px 14px; font-size: 12px; font-weight: 700; color: #64748b;
  text-transform: uppercase; letter-spacing: 0.4px; white-space: nowrap;
  text-align: center;
}
tbody tr { border-bottom: 1px solid #f1f5f9; transition: background 0.1s; }
tbody tr:last-child { border-bottom: none; }
tbody tr:hover { background: #f8fafc; }
tbody td { padding: 10px 14px; font-size: 13px; color: #1e293b; text-align: left; }
/* Vertical dividers between columns */
thead th:not(:first-child),
tbody td:not(:first-child) { border-left: 1px solid #e2e8f0; }

.row-clickable { cursor: pointer; }
.td-nowrap { white-space: nowrap; }
.td-truncate { max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.td-actions { white-space: nowrap; }
.actions-wrap { display: flex; gap: 6px; align-items: center; justify-content: center; }
.text-muted { color: #94a3b8; }

/* ── Action buttons ── */
.btn-icon {
  width: 30px;
  height: 30px;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  color: #475569;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition:
    background 0.15s,
    color 0.15s,
    border-color 0.15s;
}
.btn-icon:hover {
  background: #eff6ff;
  color: #2563eb;
  border-color: #bfdbfe;
}
.btn-danger {
  border-color: #fecaca;
  background: #fef2f2;
  color: #ef4444;
}
.btn-danger:hover {
  background: #fee2e2;
  color: #dc2626;
  border-color: #fca5a5;
}

/* ── Status badge ── */
.status-badge {
  display: inline-block;
  padding: 3px 9px;
  border-radius: 99px;
  font-size: 11px;
  font-weight: 700;
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

/* ── Jenis badge ── */
.jenis-badge {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 99px;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
}
.jenis-danger {
  background: #fee2e2;
  color: #991b1b;
}
.jenis-warning {
  background: #fef3c7;
  color: #92400e;
}
.jenis-default {
  background: #f1f5f9;
  color: #475569;
}

/* ── Photo count badge (table) ── */
.photo-count-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: #eff6ff;
  color: #2563eb;
  font-size: 12px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 99px;
  white-space: nowrap;
}
.photo-count-btn {
  border: none;
  cursor: pointer;
  transition: background 0.15s;
}
.photo-count-btn:hover {
  background: #dbeafe;
}

/* ── Delete confirm modal ── */
.modal-sm {
  max-width: 460px;
}
.modal-header-danger {
  background: #fff5f5;
  border-bottom-color: #fecaca;
}
.modal-title-group {
  display: flex;
  align-items: center;
  gap: 10px;
}
.modal-danger-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #ef4444;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.delete-modal-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.delete-msg {
  font-size: 14px;
  color: #475569;
  margin: 0;
  line-height: 1.6;
}
.delete-preview {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.delete-preview-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 13px;
  color: #334155;
}
.delete-preview-label {
  font-weight: 600;
  color: #94a3b8;
  min-width: 80px;
  flex-shrink: 0;
}
.delete-preview-desc {
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
}
.delete-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}
.btn-delete-confirm {
  background: #ef4444;
  color: #fff;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.btn-delete-confirm:hover:not(:disabled) {
  background: #dc2626;
}
.btn-delete-confirm:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* ── Toast ── */
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
.toast-enter-active {
  transition: all 0.3s ease;
}
.toast-leave-active {
  transition: all 0.25s ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(40px);
}

/* ── Loading ── */
.ci-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 60px 24px;
  color: #64748b;
  font-size: 14px;
}
.ci-spinner {
  width: 28px;
  height: 28px;
  border: 3px solid #e2e8f0;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: ci-spin 0.7s linear infinite;
}
@keyframes ci-spin {
  to {
    transform: rotate(360deg);
  }
}

/* ── Empty state ── */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 60px 24px;
  text-align: center;
  color: #64748b;
  font-size: 14px;
}
.empty-state p {
  margin: 0;
}
.btn-inline-link {
  background: none;
  border: none;
  color: #2563eb;
  cursor: pointer;
  font-size: 14px;
  text-decoration: underline;
  padding: 0;
}

/* ── Modal ── */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 16px;
  overscroll-behavior: contain;
}
.modal-container {
  background: #fff;
  border-radius: 14px;
  overflow: hidden;
  width: 100%;
  max-width: 680px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}
.modal-lg {
  max-width: 780px;
}
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px 16px;
  border-bottom: 1px solid #f1f5f9;
  flex-shrink: 0;
}
.modal-title {
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}
.modal-close {
  background: none;
  border: none;
  cursor: pointer;
  color: #94a3b8;
  padding: 4px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  transition:
    background 0.15s,
    color 0.15s;
}
.modal-close:hover {
  background: #f1f5f9;
  color: #475569;
}
.modal-body {
  overflow-y: auto;
  padding: 20px 24px 24px;
  overscroll-behavior: contain;
}
.modal-footer-bar {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  padding: 14px 24px 18px;
  border-top: 1px solid #e2e8f0;
  background: #f8fafc;
  border-radius: 0 0 14px 14px;
  flex-shrink: 0;
}

/* ── Modal transition ── */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}
.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition:
    transform 0.2s ease,
    opacity 0.2s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: translateY(-16px);
  opacity: 0;
}

/* ── Form ── */
.form-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.form-section {
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
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
  margin: 0;
}
.photo-count-label {
  font-weight: 400;
  color: #94a3b8;
  font-size: 12px;
  text-transform: none;
  letter-spacing: 0;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}
@media (max-width: 560px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 0;
}
.form-group--full {
  grid-column: 1 / -1;
}

.form-group label {
  font-size: 13px;
  font-weight: 600;
  color: #374151;
}
.required {
  color: #ef4444;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  box-sizing: border-box;
  padding: 9px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  color: #1e293b;
  background: #fff;
  transition:
    border-color 0.15s,
    box-shadow 0.15s;
  font-family: inherit;
}
.form-group select {
  cursor: pointer;
}
.form-group textarea {
  resize: vertical;
  min-height: 80px;
  line-height: 1.55;
}
.form-group input::placeholder,
.form-group textarea::placeholder {
  color: #94a3b8;
}
.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.12);
}
.form-group select:disabled,
.form-group input:disabled {
  cursor: not-allowed;
  background: #f1f5f9;
  color: #94a3b8;
  opacity: 1;
}

/* ── Pelapor (disabled) ── */
.input-pelapor {
  width: 100%;
  box-sizing: border-box;
  padding: 9px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  background: #f1f5f9;
  color: #64748b;
  cursor: not-allowed;
}

/* ── Date input wrapper ── */
.date-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}
.date-input-wrapper input[type='date'] {
  padding-right: 36px;
}
.date-icon {
  position: absolute;
  right: 10px;
  color: #94a3b8;
  cursor: pointer;
  pointer-events: auto;
}

/* ── Saksi / Petugas rows ── */
.petugas-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.petugas-row {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  align-items: center;
  gap: 8px;
}
.petugas-nama-wrap {
  position: relative;
  min-width: 0;
}
.petugas-nama-input {
  width: 100%;
  padding: 9px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  color: #1e293b;
  outline: none;
  background: #fff;
  transition: border-color 0.15s;
  box-sizing: border-box;
}
.petugas-nama-input:focus {
  border-color: #3b82f6;
}
.petugas-dept-select {
  width: 100%;
  min-width: 0;
  padding: 9px 10px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  color: #1e293b;
  background: #fff;
  outline: none;
  cursor: pointer;
}
@media (max-width: 768px) {
  .petugas-row {
    grid-template-columns: 1.2fr 1fr auto;
    gap: 6px;
  }
  .petugas-dept-select {
    padding: 9px 6px;
    font-size: 13px;
  }
}
.petugas-remove {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  border: 1px solid #fecaca;
  border-radius: 6px;
  background: #fef2f2;
  color: #ef4444;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  line-height: 1;
}
.petugas-remove:hover {
  background: #fee2e2;
}

/* ── Mention dropdown ── */
.mention-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  z-index: 2000;
  max-height: 220px;
  overflow-y: auto;
}
.mention-item {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 8px 12px;
  background: none;
  border: none;
  cursor: pointer;
  text-align: left;
  border-bottom: 1px solid #f1f5f9;
  transition: background 0.1s;
}
.mention-item:last-child {
  border-bottom: none;
}
.mention-item:hover,
.mention-item-active {
  background: #eff6ff;
}
.mention-item-active .mention-name {
  color: #2563eb;
}
.mention-name {
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
}
.mention-dept {
  font-size: 12px;
  color: #94a3b8;
  margin-left: auto;
}

/* ── Add button ── */
.bullet-add {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  align-self: flex-start;
  padding: 4px 10px;
  background: #f8fafc;
  border: 1px dashed #cbd5e1;
  border-radius: 6px;
  font-size: 12px;
  color: #475569;
  cursor: pointer;
  transition:
    background 0.15s,
    border-color 0.15s;
}
.bullet-add:hover {
  background: #f1f5f9;
  border-color: #94a3b8;
  color: #1e293b;
}

/* ── Photo upload ── */
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
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
.photo-clear {
  margin-bottom: 10px;
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
}
.btn-clear:hover {
  background: #fee2e2;
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

/* ── Detail modal ── */
.detail-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.detail-section {
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.detail-section:last-child {
  border-bottom: none;
  padding-bottom: 0;
}
.detail-row {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}
.detail-label {
  font-size: 13px;
  font-weight: 600;
  color: #64748b;
  min-width: 160px;
  flex-shrink: 0;
}
.detail-value {
  font-size: 13px;
  color: #1e293b;
  flex: 1;
}
.detail-multiline {
  white-space: pre-wrap;
  line-height: 1.6;
}
.petugas-dept-tag {
  display: inline-block;
  margin-left: 8px;
  padding: 1px 7px;
  background: #f1f5f9;
  color: #64748b;
  border-radius: 99px;
  font-size: 11px;
}
.detail-photo-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.detail-photo-thumb {
  width: 90px;
  height: 90px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  cursor: pointer;
  transition:
    opacity 0.15s,
    transform 0.15s;
}
.detail-photo-thumb:hover {
  opacity: 0.85;
  transform: scale(1.03);
}

/* ── Lightbox ── */
.lightbox-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.88);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3000;
  outline: none;
}
.lightbox-content {
  display: flex;
  align-items: center;
  justify-content: center;
  max-width: 90vw;
  max-height: 85vh;
}
.lightbox-img {
  max-width: 90vw;
  max-height: 82vh;
  object-fit: contain;
  border-radius: 6px;
}
.lightbox-close {
  position: fixed;
  top: 16px;
  right: 16px;
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.12);
  border: none;
  border-radius: 8px;
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
  z-index: 1;
}
.lightbox-close:hover {
  background: rgba(255, 255, 255, 0.22);
}
.lightbox-download {
  position: fixed;
  top: 16px;
  right: 64px;
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.12);
  border: none;
  border-radius: 8px;
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
  z-index: 1;
}
.lightbox-download:hover {
  background: rgba(255, 255, 255, 0.22);
}
.lightbox-nav {
  position: fixed;
  top: 50%;
  transform: translateY(-50%);
  width: 44px;
  height: 44px;
  background: rgba(255, 255, 255, 0.12);
  border: none;
  border-radius: 50%;
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
  z-index: 1;
}
.lightbox-nav:hover {
  background: rgba(255, 255, 255, 0.25);
}
.lightbox-prev {
  left: 16px;
}
.lightbox-next {
  right: 16px;
}
.lightbox-dots {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 8px;
}
.lightbox-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  transition: background 0.15s;
}
.lightbox-dot.active {
  background: #fff;
}
.lightbox-fade-enter-active,
.lightbox-fade-leave-active {
  transition: opacity 0.2s ease;
}
.lightbox-fade-enter-from,
.lightbox-fade-leave-to {
  opacity: 0;
}
.discard-icon {
  display: flex;
  justify-content: center;
  margin-bottom: 12px;
  color: #f59e0b;
}
.discard-title {
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
  text-align: center;
  margin: 0 0 8px;
}
.discard-desc {
  font-size: 13px;
  color: #64748b;
  text-align: center;
  margin: 0;
  line-height: 1.6;
}
.discard-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 12px 24px 20px;
  border-top: 1px solid #f1f5f9;
}
.btn-discard-confirm {
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
.btn-discard-confirm:hover {
  background: #dc2626;
}
</style>
