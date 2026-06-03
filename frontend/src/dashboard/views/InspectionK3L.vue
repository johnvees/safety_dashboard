<template>
  <div class="inspection-k3l">
    <div class="page-header">
      <div>
        <h2>Inspection K3L</h2>
        <p class="subtitle">
          Laporan inspeksi Keselamatan, Kesehatan Kerja & Lingkungan
        </p>
      </div>
      <button class="btn-primary" @click="showForm = true">
        + Tambah Temuan
      </button>
    </div>

    <!-- Scope filter row -->
    <div class="action-bar">
      <div v-if="roleLevel <= 2" class="scope-filter-inline">
        <select v-model="filterBU" class="scope-select">
          <option :value="null">Semua Business Unit</option>
          <option v-for="bu in businessUnits" :key="bu.id" :value="bu.id">
            {{ bu.name }}
          </option>
        </select>
        <select v-model="filterPlant" class="scope-select">
          <option :value="null">Semua Plant</option>
          <option v-for="p in availablePlants" :key="p.id" :value="p.id">
            {{ p.name }}
          </option>
        </select>
        <button
          v-if="filterBU || filterPlant"
          class="scope-reset-btn"
          @click="resetScopeFilter"
        >
          Atur Ulang
        </button>
      </div>
      <div v-else-if="roleLevel <= 4" class="scope-filter-inline">
        <span class="scope-bu-label">{{
          businessUnits.find((b) => b.id === currentUser.businessUnitId)
            ?.name || 'Business Unit'
        }}</span>
        <select v-model="filterPlant" class="scope-select">
          <option :value="null">Semua Plant</option>
          <option v-for="p in availablePlants" :key="p.id" :value="p.id">
            {{ p.name }}
          </option>
        </select>
        <button
          v-if="filterPlant"
          class="scope-reset-btn"
          @click="filterPlant = null"
        >
          Atur Ulang
        </button>
      </div>
    </div>

    <!-- ── Input / Edit Form Modal ── -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showForm" class="modal-overlay" @click.self="tryCloseForm">
          <div class="modal-container">
            <div class="modal-header">
              <h3 class="modal-title">
                {{ editingId ? 'Ubah Temuan' : 'Input Temuan Baru' }}
              </h3>
              <button class="modal-close" @click="tryCloseForm">
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
              <form @submit.prevent="submitForm" class="form-grid">
                <!-- Waktu -->
                <div class="form-section">
                  <h4 class="section-title">Waktu</h4>
                  <div class="form-row">
                    <div class="form-group">
                      <label>Tanggal <span class="required">*</span></label>
                      <div class="date-input-wrapper">
                        <input
                          type="datetime-local"
                          v-model="form.tanggal"
                          required
                          ref="tanggalInput"
                          @click="$refs.tanggalInput.showPicker()"
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
                </div>

                <!-- Temuan -->
                <div class="form-section">
                  <h4 class="section-title">Temuan</h4>
                  <div class="form-row">
                    <div class="form-group">
                      <label
                        >Kategori Temuan <span class="required">*</span></label
                      >
                      <select v-model="form.kategoriTemuan" required>
                        <option value="" disabled>Pilih Kategori</option>
                        <option value="Low">Low</option>
                        <option value="Medium">Medium</option>
                        <option value="High">High</option>
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

                  <!-- CREATE: foto sebelum upload -->
                  <template v-if="!editingId">
                    <div class="form-row">
                      <div class="form-group full-width">
                        <label
                          >Foto Sebelum
                          <span class="photo-count"
                            >({{ photos.length }}/10)</span
                          ></label
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
                    </div>
                  </template>

                  <!-- EDIT: foto sebelum view-only + foto sesudah upload -->
                  <template v-else>
                    <div class="form-row">
                      <div class="form-group full-width">
                        <label
                          >Foto Sebelum
                          <span class="photo-readonly-tag"
                            >Hanya Lihat</span
                          ></label
                        >
                        <div
                          v-if="photos.length > 0"
                          class="photo-readonly-grid"
                        >
                          <img
                            v-for="(photo, idx) in photos"
                            :key="idx"
                            :src="photo.preview"
                            alt="Foto sebelum"
                            class="photo-readonly-thumb"
                            @click="
                              openPhotoModalFromUrls(
                                photos.map((p) => p.preview),
                                idx,
                              )
                            "
                          />
                        </div>
                        <div v-else class="photo-empty">
                          Tidak ada foto sebelum
                        </div>
                      </div>
                    </div>
                    <div class="form-row" style="margin-top: 12px">
                      <div class="form-group full-width">
                        <label
                          >Foto Sesudah
                          <span class="photo-count"
                            >({{ photosAfter.length }}/10)</span
                          ></label
                        >
                        <div class="photo-upload">
                          <div class="photo-grid" v-if="photosAfter.length > 0">
                            <div
                              class="photo-preview"
                              v-for="(photo, idx) in photosAfter"
                              :key="idx"
                            >
                              <img :src="photo.preview" alt="Preview" />
                              <button
                                type="button"
                                class="photo-remove"
                                @click="removePhotoAfterAt(idx)"
                              >
                                x
                              </button>
                            </div>
                          </div>
                          <div
                            class="photo-clear"
                            v-if="photosAfter.length > 1"
                          >
                            <button
                              type="button"
                              class="btn btn-clear"
                              @click="clearPhotosAfter"
                            >
                              Hapus Semua Foto
                            </button>
                          </div>
                          <div
                            class="photo-actions"
                            v-if="photosAfter.length < 10"
                          >
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
                                @change="onPhotoAfterSelect"
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
                                @change="onPhotoAfterSelect"
                                style="display: none"
                              />
                            </label>
                          </div>
                        </div>
                      </div>
                    </div>
                  </template>
                </div>

                <!-- Lokasi -->
                <div class="form-section">
                  <h4 class="section-title">Lokasi</h4>
                  <div class="form-row">
                    <div class="form-group form-group-fill">
                      <label>Lokasi Temuan</label>
                      <input
                        type="text"
                        v-model="form.lokasi"
                        placeholder="Lokasi temuan"
                      />
                    </div>
                    <div class="form-group form-group-fill">
                      <label>Department</label>
                      <select v-model.number="form.departmentId">
                        <option :value="null">Pilih Department</option>
                        <option
                          v-for="dept in departments"
                          :key="dept.id"
                          :value="dept.id"
                        >
                          {{ dept.name }}
                        </option>
                      </select>
                    </div>
                  </div>
                  <div class="form-row">
                    <div class="form-group form-group-fill">
                      <template v-if="roleLevel <= 2">
                        <label>Business Unit</label>
                        <select v-model.number="form.businessUnitId">
                          <option :value="null">Pilih Business Unit</option>
                          <option
                            v-for="bu in businessUnits"
                            :key="bu.id"
                            :value="bu.id"
                          >
                            {{ bu.name }}
                          </option>
                        </select>
                      </template>
                      <template v-else>
                        <label
                          >Business Unit
                          <span class="field-auto-tag">Otomatis</span></label
                        >
                        <input
                          type="text"
                          :value="getBusinessUnitName(form.businessUnitId)"
                          disabled
                          class="field-auto"
                          placeholder="-"
                        />
                      </template>
                    </div>
                    <div class="form-group form-group-fill">
                      <template v-if="roleLevel <= 4">
                        <label>Plant</label>
                        <select v-model.number="form.plantId">
                          <option :value="null">Pilih Plant</option>
                          <option
                            v-for="p in filteredPlants"
                            :key="p.id"
                            :value="p.id"
                          >
                            {{ p.name }}
                          </option>
                        </select>
                      </template>
                      <template v-else>
                        <label
                          >Plant
                          <span class="field-auto-tag">Otomatis</span></label
                        >
                        <input
                          type="text"
                          :value="getPlantName(form.plantId)"
                          disabled
                          class="field-auto"
                          placeholder="-"
                        />
                      </template>
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
                          @click="$refs.targetSelesaiInput.showPicker()"
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
                    <div
                      class="form-group"
                      v-if="editingId && form.status === 'Closed'"
                    >
                      <label>Aktual Close</label>
                      <div class="date-input-wrapper">
                        <input
                          type="datetime-local"
                          v-model="form.aktualClose"
                          ref="aktualCloseInput"
                          @click="$refs.aktualCloseInput.showPicker()"
                        />
                        <svg
                          class="date-icon"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          stroke-width="2"
                          width="18"
                          height="18"
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
                </div>

                <!-- Submit -->
                <div class="form-actions">
                  <button
                    type="submit"
                    class="btn-primary"
                    :disabled="submitting"
                  >
                    {{
                      submitting
                        ? 'Menyimpan...'
                        : editingId
                          ? 'Perbarui'
                          : 'Simpan'
                    }}
                  </button>
                  <button
                    type="button"
                    class="btn-secondary"
                    @click="tryCloseForm"
                  >
                    Batal
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- ── View Detail Modal ── -->
    <Teleport to="body">
      <Transition name="modal">
        <div
          v-if="showViewModal && viewingRecord"
          class="modal-overlay"
          @click.self="closeViewModal()"
        >
          <div class="modal-container modal-lg">
            <div class="modal-header">
              <h3 class="modal-title">Detail Temuan</h3>
              <button class="modal-close" @click="closeViewModal()">
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
                <div class="detail-section">
                  <h4 class="section-title">Waktu</h4>
                  <div class="detail-row">
                    <span class="detail-label">Tanggal</span>
                    <span class="detail-value">{{
                      formatDate(viewingRecord.tanggal)
                    }}</span>
                  </div>
                </div>

                <div class="detail-section">
                  <h4 class="section-title">Temuan</h4>
                  <div class="detail-row">
                    <span class="detail-label">Kategori</span>
                    <span class="detail-value">
                      <span
                        :class="[
                          'kategori-badge',
                          `kategori-${viewingRecord.kategoriTemuan?.toLowerCase()}`,
                        ]"
                      >
                        {{ viewingRecord.kategoriTemuan }}
                      </span>
                    </span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">Deskripsi</span>
                    <span class="detail-value detail-multiline">{{
                      viewingRecord.deskripsiTemuan || '-'
                    }}</span>
                  </div>
                </div>

                <div
                  class="detail-section"
                  v-if="
                    parsePhotos(viewingRecord.fotoSebelum).length ||
                    parsePhotos(viewingRecord.fotoSesudah).length
                  "
                >
                  <h4 class="section-title">Foto</h4>
                  <div v-if="parsePhotos(viewingRecord.fotoSebelum).length">
                    <p class="foto-sublabel">Sebelum</p>
                    <div class="detail-photo-grid">
                      <img
                        v-for="(url, idx) in parsePhotos(
                          viewingRecord.fotoSebelum,
                        )"
                        :key="'before-' + idx"
                        :src="url"
                        alt="Foto sebelum"
                        class="detail-photo-thumb"
                        @click="
                          openPhotoModalFromUrls(
                            parsePhotos(viewingRecord.fotoSebelum),
                            idx,
                          )
                        "
                      />
                    </div>
                  </div>
                  <div
                    v-if="parsePhotos(viewingRecord.fotoSesudah).length"
                    style="margin-top: 12px"
                  >
                    <p class="foto-sublabel">Sesudah</p>
                    <div class="detail-photo-grid">
                      <img
                        v-for="(url, idx) in parsePhotos(
                          viewingRecord.fotoSesudah,
                        )"
                        :key="'after-' + idx"
                        :src="url"
                        alt="Foto sesudah"
                        class="detail-photo-thumb"
                        @click="
                          openPhotoModalFromUrls(
                            parsePhotos(viewingRecord.fotoSesudah),
                            idx,
                          )
                        "
                      />
                    </div>
                  </div>
                </div>

                <div class="detail-section">
                  <h4 class="section-title">Lokasi</h4>
                  <div class="detail-row">
                    <span class="detail-label">Lokasi</span>
                    <span class="detail-value">{{
                      viewingRecord.lokasi || '-'
                    }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">Department</span>
                    <span class="detail-value">{{
                      getDepartmentName(viewingRecord.departmentId)
                    }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">Business Unit</span>
                    <span class="detail-value">{{
                      getBusinessUnitName(viewingRecord.businessUnitId)
                    }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">Plant</span>
                    <span class="detail-value">{{
                      getPlantName(viewingRecord.plantId)
                    }}</span>
                  </div>
                </div>

                <div class="detail-section">
                  <h4 class="section-title">Tindakan</h4>
                  <div class="detail-row">
                    <span class="detail-label">Tindakan Perbaikan</span>
                    <span class="detail-value detail-multiline">{{
                      viewingRecord.tindakanPerbaikan || '-'
                    }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">Target Selesai</span>
                    <span class="detail-value">{{
                      formatDateOnly(viewingRecord.targetSelesai)
                    }}</span>
                  </div>
                </div>

                <div class="detail-section">
                  <h4 class="section-title">Status</h4>
                  <div class="detail-row">
                    <span class="detail-label">Status</span>
                    <span class="detail-value">
                      <span
                        :class="[
                          'status-badge',
                          `status-${viewingRecord.status.toLowerCase().replace(' ', '-')}`,
                        ]"
                      >
                        {{ viewingRecord.status }}
                      </span>
                    </span>
                  </div>
                  <div class="detail-row" v-if="viewingRecord.aktualClose">
                    <span class="detail-label">Aktual Close</span>
                    <span class="detail-value">{{
                      formatDate(viewingRecord.aktualClose)
                    }}</span>
                  </div>
                </div>

                <div class="detail-section detail-comments">
                  <CommentSection
                    :report-type="'inspection_k3l'"
                    :report-id="viewingRecord.id"
                    @count-change="onCommentCountChange"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- ── Photo Lightbox Modal ── -->
    <Teleport to="body">
      <Transition name="fade">
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
                <h3 class="modal-title">Hapus Data</h3>
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
                Apakah Anda yakin ingin menghapus data temuan ini? Tindakan ini
                tidak dapat dibatalkan.
              </p>
              <div v-if="deletingRecord" class="delete-preview">
                <div class="delete-preview-row">
                  <span class="delete-preview-label">Tanggal</span>
                  <span>{{ formatDate(deletingRecord.tanggal) }}</span>
                </div>
                <div class="delete-preview-row">
                  <span class="delete-preview-label">Kategori</span>
                  <span
                    :class="[
                      'kategori-badge',
                      `kategori-${deletingRecord.kategoriTemuan?.toLowerCase()}`,
                    ]"
                  >
                    {{ deletingRecord.kategoriTemuan }}
                  </span>
                </div>
                <div
                  class="delete-preview-row"
                  v-if="deletingRecord.deskripsiTemuan"
                >
                  <span class="delete-preview-label">Deskripsi</span>
                  <span class="delete-preview-desc">{{
                    deletingRecord.deskripsiTemuan
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

    <!-- Discard Confirm Dialog -->
    <Teleport to="body">
      <Transition name="modal">
        <div
          v-if="showDiscardConfirm"
          class="modal-overlay"
          style="z-index: 1100"
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
              <button class="btn-secondary" @click="showDiscardConfirm = false">
                Kembali
              </button>
              <button class="btn btn-discard-confirm" @click="forceCloseForm">
                Ya, Batalkan
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

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
        <div class="table-header-actions">
          <div
            class="export-dropdown-wrap"
            v-click-outside="() => (showExportDropdown = false)"
          >
            <button
              class="btn btn-sm btn-export"
              @click="showExportDropdown = !showExportDropdown"
              title="Pilih format ekspor"
            >
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                width="14"
                height="14"
              >
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="7 10 12 15 17 10" />
                <line x1="12" y1="15" x2="12" y2="3" />
              </svg>
              Ekspor
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                width="10"
                height="10"
                style="margin-left: 2px"
              >
                <polyline points="6 9 12 15 18 9" />
              </svg>
            </button>
            <div v-if="showExportDropdown" class="export-dropdown-menu">
              <button
                class="export-dropdown-item"
                @click="
                  exportCsv();
                  showExportDropdown = false;
                "
                :disabled="filteredRecords.length === 0"
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
                    d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"
                  />
                  <polyline points="14 2 14 8 20 8" />
                  <line x1="16" y1="13" x2="8" y2="13" />
                  <line x1="16" y1="17" x2="8" y2="17" />
                </svg>
                <div>
                  <div class="export-item-label">Excel (Semua Data)</div>
                  <div class="export-item-desc">
                    Ekspor data yang tampil saat ini
                  </div>
                </div>
              </button>
              <button
                class="export-dropdown-item"
                @click="
                  showExportModal = true;
                  showExportDropdown = false;
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
                  <rect x="3" y="4" width="18" height="18" rx="2" />
                  <line x1="16" y1="2" x2="16" y2="6" />
                  <line x1="8" y1="2" x2="8" y2="6" />
                  <line x1="3" y1="10" x2="21" y2="10" />
                </svg>
                <div>
                  <div class="export-item-label">Laporan Bulanan</div>
                  <div class="export-item-desc">
                    Ekspor Excel atau PDF per bulan
                  </div>
                </div>
              </button>
            </div>
          </div>
          <button
            class="btn btn-sm btn-summary"
            @click="openSummaryModal"
            title="Lihat ringkasan statistik bulanan"
          >
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              width="14"
              height="14"
            >
              <line x1="18" y1="20" x2="18" y2="10" />
              <line x1="12" y1="20" x2="12" y2="4" />
              <line x1="6" y1="20" x2="6" y2="14" />
            </svg>
            Ringkasan
          </button>
          <button class="btn btn-sm" @click="loadData" :disabled="loading">
            {{ loading ? 'Memuat...' : 'Segarkan' }}
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
          <input
            type="date"
            v-model="customDateFrom"
            class="toolbar-date"
            @click="$event.target.showPicker?.()"
          />
        </label>
        <span class="date-sep">–</span>
        <label class="toolbar-date-wrap">
          <input
            type="date"
            v-model="customDateTo"
            class="toolbar-date"
            @click="$event.target.showPicker?.()"
          />
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
            placeholder="Cari deskripsi, lokasi, tanggal..."
          />
          <button
            v-if="searchQuery"
            class="search-clear"
            @click="searchQuery = ''"
          >
            &times;
          </button>
        </div>

        <select v-model="filterKategori" class="filter-select">
          <option value="">Semua Kategori</option>
          <option value="Low">Low</option>
          <option value="Medium">Medium</option>
          <option value="High">High</option>
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
          Atur Ulang
        </button>

        <span v-if="hasActiveFilters" class="filter-count">
          {{ filteredRecords.length }} / {{ scopedRecords.length }} data
        </span>
      </div>

      <div class="table-wrapper">
        <table v-if="pagedRecords.length > 0">
          <thead>
            <tr>
              <th style="text-align: center; width: 48px">No</th>
              <th>Tanggal</th>
              <th>Kategori Temuan</th>
              <th>Deskripsi Temuan</th>
              <th>Foto Sebelum</th>
              <th>Foto Sesudah</th>
              <th>Lokasi</th>
              <th>Department</th>
              <th>Business Unit</th>
              <th>Plant</th>
              <th>Tindakan Perbaikan</th>
              <th>Target Selesai</th>
              <th>Aktual Close</th>
              <th>Status</th>
              <th style="text-align: center">Komentar</th>
              <th>Aksi</th>
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
                {{ (k3lCurrentPage - 1) * k3lPerPage + idx + 1 }}
              </td>
              <td class="td-nowrap">{{ formatDate(item.tanggal) }}</td>
              <td>
                <span
                  :class="[
                    'kategori-badge',
                    `kategori-${item.kategoriTemuan?.toLowerCase()}`,
                  ]"
                >
                  {{ item.kategoriTemuan }}
                </span>
              </td>
              <td class="td-truncate">{{ item.deskripsiTemuan || '-' }}</td>
              <td class="td-center" @click.stop>
                <button
                  v-if="parsePhotos(item.fotoSebelum).length"
                  class="btn-icon btn-eye"
                  title="Lihat Foto Sebelum"
                  @click="
                    openPhotoModalFromUrls(parsePhotos(item.fotoSebelum), 0)
                  "
                >
                  <svg
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    width="16"
                    height="16"
                  >
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                    <circle cx="12" cy="12" r="3" />
                  </svg>
                  <span class="photo-count-badge">{{
                    parsePhotos(item.fotoSebelum).length
                  }}</span>
                </button>
                <span v-else class="text-muted">-</span>
              </td>
              <td class="td-center" @click.stop>
                <button
                  v-if="parsePhotos(item.fotoSesudah).length"
                  class="btn-icon btn-eye btn-eye-after"
                  title="Lihat Foto Sesudah"
                  @click="
                    openPhotoModalFromUrls(parsePhotos(item.fotoSesudah), 0)
                  "
                >
                  <svg
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    width="16"
                    height="16"
                  >
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                    <circle cx="12" cy="12" r="3" />
                  </svg>
                  <span class="photo-count-badge photo-count-badge-after">{{
                    parsePhotos(item.fotoSesudah).length
                  }}</span>
                </button>
                <span v-else class="text-muted">-</span>
              </td>
              <td class="td-nowrap">{{ item.lokasi || '-' }}</td>
              <td class="td-nowrap">
                {{ getDepartmentName(item.departmentId) }}
              </td>
              <td class="td-nowrap">
                {{ getBusinessUnitName(item.businessUnitId) }}
              </td>
              <td class="td-nowrap">{{ getPlantName(item.plantId) }}</td>
              <td class="td-truncate">{{ item.tindakanPerbaikan || '-' }}</td>
              <td class="td-nowrap">
                {{ formatDateOnly(item.targetSelesai) }}
              </td>
              <td class="td-nowrap">{{ formatDate(item.aktualClose) }}</td>
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
              <td class="td-center">
                <span
                  class="comment-badge"
                  :class="{ 'has-comments': (item.commentCount || 0) > 0 }"
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
                      d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"
                    />
                  </svg>
                  {{ item.commentCount || 0 }}
                </span>
              </td>
              <td class="td-actions" @click.stop>
                <div class="actions-wrap">
                <button class="btn-icon" title="Ubah" @click="editRecord(item)">
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
            </tr>
          </tbody>
        </table>
      </div>
      <PaginationBar
        v-if="pagedRecords.length > 0"
        :current-page="k3lCurrentPage"
        :total-pages="k3lTotalPages"
        :total-items="k3lTotalItems"
        :per-page="k3lPerPage"
        @page="k3lGoToPage"
        @per-page="k3lSetPerPage"
      />
      <div v-else-if="hasActiveFilters" class="empty-state">
        <p>
          Tidak ada data yang cocok dengan filter.
          <button class="btn-inline-link" @click="resetFilters">
            Atur ulang filter
          </button>
        </p>
      </div>
      <div v-else class="empty-state">
        <p>Belum ada data temuan. Klik "Tambah Temuan" untuk menambahkan.</p>
      </div>
    </div>

    <!-- ── Modal: Export Bulanan (Option 1 + PDF) ──────────────────────── -->
    <div
      v-if="showExportModal"
      class="modal-overlay"
      @click.self="showExportModal = false"
    >
      <div class="modal-container modal-export-monthly">
        <div class="modal-header">
          <h3 class="modal-title">Ekspor Data Bulanan</h3>
          <button class="modal-close" @click="showExportModal = false">
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
        <div class="modal-body">
          <p class="modal-desc">
            Pilih bulan dan tahun untuk mengekspor data Inspection K3L.
          </p>
          <div class="export-month-row">
            <div class="export-field">
              <label class="export-label">Bulan</label>
              <select v-model="exportMonth" class="export-select">
                <option
                  v-for="(name, idx) in MONTH_NAMES"
                  :key="idx + 1"
                  :value="idx + 1"
                >
                  {{ name }}
                </option>
              </select>
            </div>
            <div class="export-field">
              <label class="export-label">Tahun</label>
              <select v-model="exportYear" class="export-select">
                <option
                  v-for="y in Array.from(
                    { length: 5 },
                    (_, i) => new Date().getFullYear() - i,
                  )"
                  :key="y"
                  :value="y"
                >
                  {{ y }}
                </option>
              </select>
            </div>
          </div>
          <div class="export-preview-text">
            Ekspor data bulan
            <strong>{{ MONTH_NAMES[exportMonth - 1] }} {{ exportYear }}</strong>
          </div>
        </div>
        <div class="modal-footer-bar">
          <button class="btn-secondary" @click="showExportModal = false">
            Batal
          </button>
          <div class="export-btn-group">
            <button
              class="btn btn-export-csv"
              @click="exportMonthlyCSV"
              title="Download sebagai file Excel"
            >
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                width="13"
                height="13"
              >
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="7 10 12 15 17 10" />
                <line x1="12" y1="15" x2="12" y2="3" />
              </svg>
              Excel
            </button>
            <button
              class="btn btn-export-pdf"
              @click="downloadMonthlyPDF(exportMonth, exportYear, true)"
              :disabled="pdfGenerating"
              title="Download sebagai file PDF"
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
                  d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"
                />
                <polyline points="14 2 14 8 20 8" />
              </svg>
              {{ pdfGenerating ? 'Membuat...' : 'PDF' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Modal: Ringkasan Bulanan (Option 2) ──────────────────────────── -->
    <div
      v-if="showSummaryModal"
      class="modal-overlay"
      @click.self="showSummaryModal = false"
    >
      <div class="modal-container modal-summary">
        <div class="modal-header">
          <h3 class="modal-title">Ringkasan Bulanan — Inspection K3L</h3>
          <button class="modal-close" @click="showSummaryModal = false">
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
        <div class="modal-body">
          <!-- Month/year selector -->
          <div class="summary-month-row">
            <select
              v-model="summaryMonth"
              class="export-select"
              @change="renderSummaryCharts"
            >
              <option
                v-for="(name, idx) in MONTH_NAMES"
                :key="idx + 1"
                :value="idx + 1"
              >
                {{ name }}
              </option>
            </select>
            <select
              v-model="summaryYear"
              class="export-select"
              @change="renderSummaryCharts"
            >
              <option
                v-for="y in Array.from(
                  { length: 5 },
                  (_, i) => new Date().getFullYear() - i,
                )"
                :key="y"
                :value="y"
              >
                {{ y }}
              </option>
            </select>
          </div>

          <!-- KPI Cards -->
          <div class="kpi-row">
            <div class="kpi-card kpi-total">
              <span class="kpi-value">{{ summaryData.total }}</span>
              <span class="kpi-label">Total</span>
            </div>
            <div class="kpi-card kpi-open">
              <span class="kpi-value">{{ summaryData.open }}</span>
              <span class="kpi-label">Terbuka</span>
            </div>
            <div class="kpi-card kpi-inprogress">
              <span class="kpi-value">{{ summaryData.inProgress }}</span>
              <span class="kpi-label">Dalam Proses</span>
            </div>
            <div class="kpi-card kpi-closed">
              <span class="kpi-value">{{ summaryData.closed }}</span>
              <span class="kpi-label">Selesai</span>
            </div>
            <div class="kpi-card kpi-overdue">
              <span class="kpi-value">{{ summaryData.overdue }}</span>
              <span class="kpi-label">Terlambat</span>
            </div>
          </div>

          <!-- Charts -->
          <div v-if="summaryData.total > 0" class="charts-row">
            <div class="chart-wrap">
              <h4 class="chart-title">Temuan per Kategori</h4>
              <canvas ref="summaryChartKategoriRef" height="200"></canvas>
            </div>
            <div class="chart-wrap">
              <h4 class="chart-title">Distribusi Status</h4>
              <canvas ref="summaryChartStatusRef" height="200"></canvas>
            </div>
          </div>
          <div v-else class="empty-state">
            <p>
              Tidak ada data untuk {{ MONTH_NAMES[summaryMonth - 1] }}
              {{ summaryYear }}.
            </p>
          </div>
        </div>
        <div class="modal-footer-bar">
          <button class="btn-secondary" @click="showSummaryModal = false">
            Tutup
          </button>
          <button
            class="btn btn-export-pdf"
            @click="downloadMonthlyPDF(summaryMonth, summaryYear, false)"
            :disabled="pdfGenerating"
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
                d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"
              />
              <polyline points="14 2 14 8 20 8" />
            </svg>
            {{ pdfGenerating ? 'Membuat...' : 'Unduh PDF' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  ref,
  reactive,
  computed,
  onMounted,
  onBeforeUnmount,
  nextTick,
  watch,
} from 'vue';
import { useRoute, useRouter } from 'vue-router';
import {
  inspectionK3LService,
  uploadImage,
} from '@/services/inspectionK3LService.js';
import { exportToCsv } from '@/services/exportCsvService.js';
import { authService } from '@/services/authService.js';
import { usePagination } from '@/composables/usePagination.js';
import PaginationBar from '@/components/PaginationBar.vue';
import CommentSection from '@/components/CommentSection.vue';
import Chart from 'chart.js/auto';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

const vClickOutside = {
  mounted(el, binding) {
    el._clickOutsideHandler = (e) => {
      if (!el.contains(e.target)) binding.value(e);
    };
    document.addEventListener('mousedown', el._clickOutsideHandler);
  },
  unmounted(el) {
    document.removeEventListener('mousedown', el._clickOutsideHandler);
  },
};

const currentUser = authService.getCurrentUser();
const roleLevel = authService.getRoleLevel();

const route = useRoute();
const router = useRouter();

const showForm = ref(false);
const submitting = ref(false);
const loading = ref(false);
const editingId = ref(null);
const showDiscardConfirm = ref(false);
const originalForm = ref(null);
const records = ref([]);
const businessUnits = ref([]);
const plants = ref([]);
const departments = ref([]);

const filteredPlants = computed(() => {
  if (!form.value.businessUnitId) return [];
  return plants.value.filter(
    (p) => p.businessUnitId === form.value.businessUnitId,
  );
});

// ── Scope filter (BU + Plant) ──
const filterBU = ref(null);
const filterPlant = ref(null);
const availablePlants = ref([]);

watch(filterBU, async (newBuId) => {
  filterPlant.value = null;
  availablePlants.value = await inspectionK3LService.listPlants(newBuId);
});


const scopedRecords = computed(() => {
  let src = records.value;
  if (roleLevel >= 5) {
    src = src.filter(
      (r) =>
        Number(r.businessUnitId) === Number(currentUser?.businessUnitId) &&
        Number(r.plantId) === Number(currentUser?.plantId),
    );
  } else if (roleLevel >= 3) {
    src = src.filter(
      (r) => Number(r.businessUnitId) === Number(currentUser?.businessUnitId),
    );
    if (filterPlant.value != null)
      src = src.filter((r) => Number(r.plantId) === Number(filterPlant.value));
  } else {
    if (filterBU.value != null)
      src = src.filter(
        (r) => Number(r.businessUnitId) === Number(filterBU.value),
      );
    if (filterPlant.value != null)
      src = src.filter((r) => Number(r.plantId) === Number(filterPlant.value));
  }
  return src;
});

function resetScopeFilter() {
  filterBU.value = null;
  filterPlant.value = null;
}

// ── Search & filters ──
const searchQuery = ref('');
const filterKategori = ref('');
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

const hasActiveFilters = computed(
  () =>
    searchQuery.value.trim() !== '' ||
    filterKategori.value !== '' ||
    filterStatus.value !== '' ||
    filterDate.value !== 'all' ||
    (roleLevel <= 2 && (filterBU.value != null || filterPlant.value != null)) ||
    (roleLevel >= 3 && roleLevel < 5 && filterPlant.value != null),
);

const filteredRecords = computed(() => {
  let result = scopedRecords.value;

  if (filterKategori.value) {
    result = result.filter((r) => r.kategoriTemuan === filterKategori.value);
  }

  if (filterStatus.value) {
    result = result.filter((r) => r.status === filterStatus.value);
  }

  const q = searchQuery.value.trim().toLowerCase();
  if (q) {
    result = result.filter(
      (r) =>
        (r.deskripsiTemuan || '').toLowerCase().includes(q) ||
        (r.lokasi || '').toLowerCase().includes(q) ||
        (r.tindakanPerbaikan || '').toLowerCase().includes(q) ||
        (r.tanggal || '').includes(q) ||
        (r.kategoriTemuan || '').toLowerCase().includes(q) ||
        (r.status || '').toLowerCase().includes(q),
    );
  }

  if (filterDate.value !== 'all') {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    result = result.filter((r) => {
      if (!r.tanggal) return false;
      const d = new Date(r.tanggal);
      d.setHours(0, 0, 0, 0);
      if (filterDate.value === 'today') return d.getTime() === today.getTime();
      if (filterDate.value === 'week') {
        const start = new Date(today);
        start.setDate(today.getDate() - today.getDay());
        const end = new Date(start);
        end.setDate(start.getDate() + 6);
        return d >= start && d <= end;
      }
      if (filterDate.value === 'month')
        return (
          d.getMonth() === today.getMonth() &&
          d.getFullYear() === today.getFullYear()
        );
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
    });
  }

  return result;
});

const {
  currentPage: k3lCurrentPage,
  perPage: k3lPerPage,
  totalItems: k3lTotalItems,
  totalPages: k3lTotalPages,
  paginatedItems: pagedRecords,
  goToPage: k3lGoToPage,
  setPerPage: k3lSetPerPage,
} = usePagination(filteredRecords);

function resetFilters() {
  searchQuery.value = '';
  filterKategori.value = '';
  filterStatus.value = '';
  filterDate.value = 'all';
  customDateFrom.value = '';
  customDateTo.value = '';
  resetScopeFilter();
}

// ── View detail modal ──
const showViewModal = ref(false);
const viewingRecord = ref(null);

function viewRecord(item) {
  viewingRecord.value = item;
  showViewModal.value = true;
}

function closeViewModal() {
  showViewModal.value = false;
  viewingRecord.value = null;
  if (route.query.view) router.replace({ query: {} });
}

function onCommentCountChange(count) {
  if (!viewingRecord.value) return;
  viewingRecord.value.commentCount = count;
  const idx = records.value.findIndex((r) => r.id === viewingRecord.value.id);
  if (idx !== -1)
    records.value[idx] = { ...records.value[idx], commentCount: count };
}

// ── Photo lightbox ──
const showPhotoModal = ref(false);
const photoModalImages = ref([]);
const photoModalIndex = ref(0);

function parsePhotos(fotoSebelum) {
  if (!fotoSebelum) return [];
  try {
    const parsed = JSON.parse(fotoSebelum);
    return Array.isArray(parsed) ? parsed : [fotoSebelum];
  } catch {
    return [fotoSebelum];
  }
}

function openPhotoModalFromUrls(urls, idx) {
  photoModalImages.value = urls;
  photoModalIndex.value = idx;
  showPhotoModal.value = true;
  nextTick(() => document.querySelector('.lightbox-overlay')?.focus());
}

// ── Lookup helpers ──
function getBusinessUnitName(id) {
  if (!id) return '-';
  return businessUnits.value.find((u) => u.id === id)?.name ?? '-';
}

function getPlantName(id) {
  if (!id) return '-';
  return plants.value.find((p) => p.id === id)?.name ?? '-';
}

function getDepartmentName(id) {
  if (!id) return '-';
  return departments.value.find((d) => d.id === id)?.name ?? '-';
}

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

function formatDateOnly(val) {
  if (!val) return '-';
  const d = new Date(val.replace(' ', 'T'));
  if (isNaN(d)) return val;
  const dd = String(d.getDate()).padStart(2, '0');
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const yyyy = d.getFullYear();
  return `${dd}/${mm}/${yyyy}`;
}

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

function showMessage(msg, type = 'success') {
  showToast(msg, type);
}

// ── Photo upload (form) ──
const photos = ref([]);
const photosAfter = ref([]);

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

function onPhotoAfterSelect(event) {
  const files = Array.from(event.target.files);
  if (!files.length) return;
  const remaining = 10 - photosAfter.value.length;
  if (files.length > remaining) {
    event.target.value = '';
    showToast(
      `Maksimal 10 foto. Anda hanya dapat menambahkan ${remaining} foto lagi.`,
      'warning',
    );
    return;
  }
  for (const file of files) {
    photosAfter.value.push({ file, preview: URL.createObjectURL(file) });
  }
  event.target.value = '';
}

function removePhotoAfterAt(idx) {
  const photo = photosAfter.value[idx];
  if (photo.preview?.startsWith('blob:')) URL.revokeObjectURL(photo.preview);
  photosAfter.value.splice(idx, 1);
}

function clearPhotosAfter() {
  photosAfter.value.forEach((p) => {
    if (p.preview?.startsWith('blob:')) URL.revokeObjectURL(p.preview);
  });
  photosAfter.value = [];
}

// ── Form ──
const defaultForm = () => ({
  tanggal: '',
  kategoriTemuan: '',
  deskripsiTemuan: '',
  lokasi: '',
  tindakanPerbaikan: '',
  targetSelesai: '',
  status: 'Open',
  aktualClose: '',
  businessUnitId: currentUser?.businessUnitId ?? null,
  plantId: currentUser?.plantId ?? null,
  departmentId: null,
});

const form = ref(defaultForm());

watch(
  () => form.value.businessUnitId,
  () => {
    if (roleLevel <= 2) {
      const valid = filteredPlants.value.find(
        (p) => p.id === form.value.plantId,
      );
      if (!valid) form.value.plantId = null;
    }
  },
);

function hasFormChanges() {
  if (!editingId.value) {
    const f = form.value;
    return !!(
      f.tanggal ||
      f.kategoriTemuan ||
      f.deskripsiTemuan ||
      f.lokasi ||
      f.tindakanPerbaikan ||
      f.targetSelesai ||
      f.businessUnitId ||
      f.plantId ||
      f.departmentId ||
      photos.value.length > 0
    );
  } else {
    if (!originalForm.value) return false;
    const f = form.value;
    const o = originalForm.value;
    return (
      f.tanggal !== o.tanggal ||
      f.kategoriTemuan !== o.kategoriTemuan ||
      f.deskripsiTemuan !== o.deskripsiTemuan ||
      f.lokasi !== o.lokasi ||
      f.tindakanPerbaikan !== o.tindakanPerbaikan ||
      f.targetSelesai !== o.targetSelesai ||
      f.status !== o.status ||
      f.businessUnitId !== o.businessUnitId ||
      f.plantId !== o.plantId ||
      f.departmentId !== o.departmentId ||
      photosAfter.value.some((p) => p.file !== null)
    );
  }
}

function tryCloseForm() {
  if (submitting.value) return;
  if (hasFormChanges()) {
    showDiscardConfirm.value = true;
  } else {
    cancelForm();
  }
}

function forceCloseForm() {
  showDiscardConfirm.value = false;
  cancelForm();
}

function cancelForm() {
  showForm.value = false;
  editingId.value = null;
  form.value = defaultForm();
  originalForm.value = null;
  showDiscardConfirm.value = false;
  clearPhotos();
  clearPhotosAfter();
}

// ── Data loading ──
async function loadData() {
  loading.value = true;
  try {
    records.value = await inspectionK3LService.list();
  } catch (e) {
    console.error('[InspectionK3L] loadData:', e);
  } finally {
    loading.value = false;
  }
}

async function loadLocationOptions() {
  try {
    const [units, plantOptions, deptOptions] = await Promise.all([
      inspectionK3LService.listBusinessUnits(),
      inspectionK3LService.listPlants(),
      inspectionK3LService.listDepartments(),
    ]);
    businessUnits.value = units;
    plants.value = plantOptions;
    departments.value = deptOptions;
  } catch (e) {
    console.error('[InspectionK3L] loadLocationOptions:', e);
  }
}

async function uploadPhotoList(photoList, isCreate = false) {
  if (!photoList.length) return isCreate ? null : JSON.stringify([]);
  const urls = [];
  for (const photo of photoList) {
    if (photo.file) {
      urls.push(await uploadImage(photo.file));
    } else if (photo.preview) {
      urls.push(photo.preview);
    }
  }
  return JSON.stringify(urls);
}

async function submitForm() {
  submitting.value = true;
  try {
    const base = {
      tanggal: form.value.tanggal,
      kategoriTemuan: form.value.kategoriTemuan,
      deskripsiTemuan: form.value.deskripsiTemuan || null,
      lokasi: form.value.lokasi || null,
      tindakanPerbaikan: form.value.tindakanPerbaikan || null,
      targetSelesai: form.value.targetSelesai || null,
      status: form.value.status || 'Open',
      aktualClose:
        form.value.status === 'Closed' ? form.value.aktualClose || null : null,
      businessUnitId: form.value.businessUnitId || null,
      plantId: form.value.plantId || null,
      departmentId: form.value.departmentId || null,
    };

    if (editingId.value) {
      const fotoSesudah = await uploadPhotoList(photosAfter.value, false);
      await inspectionK3LService.update(editingId.value, {
        ...base,
        fotoSebelum: null,
        fotoSesudah,
      });
      showMessage('Data berhasil diupdate');
    } else {
      const fotoSebelum = await uploadPhotoList(photos.value, true);
      await inspectionK3LService.create({
        ...base,
        fotoSebelum,
        fotoSesudah: null,
      });
      showMessage('Data berhasil disimpan');
    }
    cancelForm();
    await loadData();
  } catch (e) {
    console.error('[InspectionK3L] submitForm:', e);
  } finally {
    submitting.value = false;
  }
}

function editRecord(item) {
  editingId.value = item.id;
  const formValues = {
    tanggal: item.tanggal ? item.tanggal.replace(' ', 'T').slice(0, 16) : '',
    kategoriTemuan: item.kategoriTemuan,
    deskripsiTemuan: item.deskripsiTemuan || '',
    lokasi: item.lokasi || '',
    tindakanPerbaikan: item.tindakanPerbaikan || '',
    targetSelesai: item.targetSelesai || '',
    status: item.status,
    aktualClose: item.aktualClose
      ? item.aktualClose.replace(' ', 'T').slice(0, 16)
      : item.status === 'Closed'
        ? (() => {
            const now = new Date();
            return new Date(now.getTime() - now.getTimezoneOffset() * 60000)
              .toISOString()
              .slice(0, 16);
          })()
        : '',
    businessUnitId: item.businessUnitId || null,
    plantId: item.plantId || null,
    departmentId: item.departmentId || null,
  };
  form.value = { ...formValues };
  originalForm.value = { ...formValues };
  clearPhotos();
  clearPhotosAfter();
  if (item.fotoSebelum) {
    photos.value = parsePhotos(item.fotoSebelum).map((url) => ({
      file: null,
      preview: url,
    }));
  }
  if (item.fotoSesudah) {
    photosAfter.value = parsePhotos(item.fotoSesudah).map((url) => ({
      file: null,
      preview: url,
    }));
  }
  showForm.value = true;
}

// ── Delete modal ──
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
    await inspectionK3LService.delete(deletingRecord.value.id);
    showMessage('Data berhasil dihapus');
    showDeleteModal.value = false;
    deletingRecord.value = null;
    await loadData();
  } catch (e) {
    console.error('[InspectionK3L] confirmDelete:', e);
  } finally {
    deleting.value = false;
  }
}

function buildK3LExport(source) {
  const parsedBefore = source.map((r) => parsePhotos(r.fotoSebelum));
  const parsedAfter = source.map((r) => parsePhotos(r.fotoSesudah));
  const maxBefore = Math.max(
    parsedBefore.reduce((m, p) => Math.max(m, p.length), 0),
    1,
  );
  const maxAfter = Math.max(
    parsedAfter.reduce((m, p) => Math.max(m, p.length), 0),
    1,
  );

  const beforeCols = Array.from({ length: maxBefore }, (_, i) => ({
    label: maxBefore === 1 ? 'Foto Sebelum' : `Foto Sebelum ${i + 1}`,
    key: `sb_${i}`,
    image: true,
  }));
  const afterCols = Array.from({ length: maxAfter }, (_, i) => ({
    label: maxAfter === 1 ? 'Foto Sesudah' : `Foto Sesudah ${i + 1}`,
    key: `sa_${i}`,
    image: true,
  }));

  const columns = [
    { label: 'No', key: 'no' },
    { label: 'Bulan', key: 'bulan' },
    { label: 'Tanggal', key: 'tanggal' },
    ...beforeCols,
    ...afterCols,
    { label: 'Lokasi', key: 'lokasi' },
    { label: 'Deskripsi Temuan', key: 'deskripsiTemuan' },
    { label: 'Tindakan Perbaikan', key: 'tindakanPerbaikan' },
    { label: 'Target Selesai', key: 'targetSelesai' },
    { label: 'Status', key: 'status' },
    { label: 'Aktual Close', key: 'aktualClose' },
    { label: 'Department', key: 'department' },
    { label: 'Plant', key: 'plant' },
    { label: 'Business Unit', key: 'businessUnit' },
  ];

  const rows = source.map((row, idx) => {
    const before = parsedBefore[idx];
    const after = parsedAfter[idx];
    const sbFields = {};
    for (let i = 0; i < maxBefore; i++) sbFields[`sb_${i}`] = before[i] || '';
    const saFields = {};
    for (let i = 0; i < maxAfter; i++) saFields[`sa_${i}`] = after[i] || '';
    return {
      no: idx + 1,
      bulan: row.tanggal ? MONTH_NAMES[new Date(row.tanggal).getMonth()] : '',
      tanggal: row.tanggal || '',
      ...sbFields,
      ...saFields,
      lokasi: row.lokasi || '',
      deskripsiTemuan: row.deskripsiTemuan || '',
      tindakanPerbaikan: row.tindakanPerbaikan || '',
      targetSelesai: row.targetSelesai || '',
      status: row.status || '',
      aktualClose: row.aktualClose || '',
      department: getDepartmentName(row.departmentId),
      plant: getPlantName(row.plantId),
      businessUnit: getBusinessUnitName(row.businessUnitId),
    };
  });

  return { columns, rows };
}

async function exportCsv() {
  const { columns, rows } = buildK3LExport(filteredRecords.value);
  const today = new Date().toISOString().slice(0, 10);
  await exportToCsv(`inspection-k3l-${today}.xlsx`, columns, rows);
}

// ── Monthly Export (Option 1) ──────────────────────────────────────────────
const showExportModal = ref(false);
const showExportDropdown = ref(false);
const exportMonth = ref(new Date().getMonth() + 1);
const exportYear = ref(new Date().getFullYear());

const MONTH_NAMES = [
  'Januari',
  'Februari',
  'Maret',
  'April',
  'Mei',
  'Juni',
  'Juli',
  'Agustus',
  'September',
  'Oktober',
  'November',
  'Desember',
];

async function exportMonthlyCSV() {
  const m = Number(exportMonth.value);
  const y = Number(exportYear.value);
  const rows = records.value.filter((r) => {
    if (!r.tanggal) return false;
    const d = new Date(r.tanggal);
    return d.getMonth() + 1 === m && d.getFullYear() === y;
  });
  if (!rows.length) {
    alert(`Tidak ada data untuk ${MONTH_NAMES[m - 1]} ${y}.`);
    return;
  }
  const { columns, rows: mapped } = buildK3LExport(rows);
  await exportToCsv(
    `inspection-k3l-${y}-${String(m).padStart(2, '0')}.xlsx`,
    columns,
    mapped,
  );
  showExportModal.value = false;
}

// ── Monthly Summary (Option 2) ─────────────────────────────────────────────
const showSummaryModal = ref(false);
const summaryMonth = ref(new Date().getMonth() + 1);
const summaryYear = ref(new Date().getFullYear());
const summaryChartKategoriRef = ref(null);
const summaryChartStatusRef = ref(null);
let chartKategori = null;
let chartStatus = null;

const summaryData = computed(() => {
  const m = Number(summaryMonth.value);
  const y = Number(summaryYear.value);
  const rows = records.value.filter((r) => {
    if (!r.tanggal) return false;
    const d = new Date(r.tanggal);
    return d.getMonth() + 1 === m && d.getFullYear() === y;
  });
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const overdue = rows.filter(
    (r) =>
      r.status !== 'Closed' &&
      r.targetSelesai &&
      new Date(r.targetSelesai) < today,
  ).length;
  const byKategori = { Low: 0, Medium: 0, High: 0 };
  const byStatus = { Open: 0, 'In Progress': 0, Closed: 0 };
  rows.forEach((r) => {
    if (r.kategoriTemuan in byKategori) byKategori[r.kategoriTemuan]++;
    if (r.status in byStatus) byStatus[r.status]++;
    else byStatus[r.status] = (byStatus[r.status] || 0) + 1;
  });
  return {
    total: rows.length,
    open: byStatus['Open'] || 0,
    inProgress: byStatus['In Progress'] || 0,
    closed: byStatus['Closed'] || 0,
    overdue,
    byKategori,
    byStatus,
    rows,
  };
});

function destroyCharts() {
  if (chartKategori) {
    chartKategori.destroy();
    chartKategori = null;
  }
  if (chartStatus) {
    chartStatus.destroy();
    chartStatus = null;
  }
}

async function openSummaryModal() {
  showSummaryModal.value = true;
  await nextTick();
  renderSummaryCharts();
}

function renderSummaryCharts() {
  destroyCharts();
  const sd = summaryData.value;
  if (summaryChartKategoriRef.value) {
    chartKategori = new Chart(summaryChartKategoriRef.value, {
      type: 'bar',
      data: {
        labels: Object.keys(sd.byKategori),
        datasets: [
          {
            label: 'Jumlah Temuan',
            data: Object.values(sd.byKategori),
            backgroundColor: ['#22c55e', '#f59e0b', '#ef4444'],
            borderRadius: 6,
            borderSkipped: false,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } },
      },
    });
  }
  if (summaryChartStatusRef.value) {
    chartStatus = new Chart(summaryChartStatusRef.value, {
      type: 'doughnut',
      data: {
        labels: ['Open', 'In Progress', 'Closed'],
        datasets: [
          {
            data: [
              sd.byStatus['Open'] || 0,
              sd.byStatus['In Progress'] || 0,
              sd.byStatus['Closed'] || 0,
            ],
            backgroundColor: ['#ef4444', '#f59e0b', '#22c55e'],
            hoverOffset: 6,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: { legend: { position: 'bottom' } },
      },
    });
  }
}

watch([summaryMonth, summaryYear], async () => {
  if (showSummaryModal.value) {
    await nextTick();
    renderSummaryCharts();
  }
});

watch(
  () => form.value.status,
  (newStatus) => {
    if (newStatus === 'Closed' && !form.value.aktualClose) {
      const now = new Date();
      form.value.aktualClose = new Date(
        now.getTime() - now.getTimezoneOffset() * 60000,
      )
        .toISOString()
        .slice(0, 16);
    } else if (newStatus !== 'Closed') {
      form.value.aktualClose = '';
    }
  },
);

// ── Download Monthly PDF (Option 3) ────────────────────────────────────────
const pdfGenerating = ref(false);

async function downloadMonthlyPDF(month, year, closeModal = false) {
  pdfGenerating.value = true;
  try {
    const m = Number(month);
    const y = Number(year);
    const monthRows = records.value
      .filter((r) => {
        if (!r.tanggal) return false;
        const d = new Date(r.tanggal);
        return d.getMonth() + 1 === m && d.getFullYear() === y;
      })
      .sort((a, b) => new Date(a.tanggal) - new Date(b.tanggal));

    const todayDate = new Date();
    todayDate.setHours(0, 0, 0, 0);
    const fmtDate = (v) => {
      if (!v) return '-';
      const d = new Date(v);
      return isNaN(d)
        ? v
        : d.toLocaleDateString('id-ID', {
            day: '2-digit',
            month: 'short',
            year: 'numeric',
          });
    };

    const total = monthRows.length;
    const open = monthRows.filter((r) => r.status === 'Open').length;
    const inProg = monthRows.filter((r) => r.status === 'In Progress').length;
    const closed = monthRows.filter((r) => r.status === 'Closed').length;
    const overdue = monthRows.filter(
      (r) =>
        r.status !== 'Closed' &&
        r.targetSelesai &&
        new Date(r.targetSelesai) < todayDate,
    ).length;

    const doc = new jsPDF({
      orientation: 'landscape',
      unit: 'mm',
      format: 'a4',
    });
    const pageW = doc.internal.pageSize.getWidth();

    // Header bar
    doc.setFillColor(30, 58, 95);
    doc.rect(0, 0, pageW, 22, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.text('LAPORAN BULANAN INSPEKSI K3L', pageW / 2, 10, {
      align: 'center',
    });
    doc.setFontSize(9);
    doc.setFont('helvetica', 'normal');
    doc.text(
      `PT Charoen Pokphand Indonesia  |  Periode: ${MONTH_NAMES[m - 1]} ${y}`,
      pageW / 2,
      17,
      { align: 'center' },
    );

    // Generated date
    doc.setTextColor(100, 116, 139);
    doc.setFontSize(8);
    const genDate = new Date().toLocaleDateString('id-ID', {
      day: '2-digit',
      month: 'long',
      year: 'numeric',
    });
    doc.text(`Dibuat: ${genDate}`, pageW - 14, 27, { align: 'right' });

    // KPI summary table
    doc.setTextColor(30, 41, 59);
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    doc.text('RINGKASAN EKSEKUTIF', 14, 34);

    autoTable(doc, {
      startY: 37,
      head: [
        [
          'Total Temuan',
          'Open',
          'In Progress',
          'Closed',
          'Overdue',
          'Close Rate',
        ],
      ],
      body: [
        [
          total,
          open,
          inProg,
          closed,
          overdue,
          `${total > 0 ? Math.round((closed / total) * 100) : 0}%`,
        ],
      ],
      theme: 'grid',
      headStyles: {
        fillColor: [30, 58, 95],
        textColor: 255,
        fontStyle: 'bold',
        fontSize: 9,
        halign: 'center',
      },
      bodyStyles: { fontSize: 11, fontStyle: 'bold', halign: 'center' },
      columnStyles: {
        0: { cellWidth: 35 },
        1: { textColor: [220, 38, 38] },
        2: { textColor: [217, 119, 6] },
        3: { textColor: [22, 163, 74] },
        4: { textColor: [147, 51, 234] },
        5: { textColor: [2, 132, 199] },
      },
      margin: { left: 14, right: 14 },
    });

    // Breakdown by kategori
    const breakdownY = doc.lastAutoTable.finalY + 8;
    doc.setTextColor(30, 41, 59);
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    doc.text('BREAKDOWN PER KATEGORI', 14, breakdownY);

    const breakdownRows = ['Low', 'Medium', 'High'].map((k) => {
      const rows = monthRows.filter((r) => r.kategoriTemuan === k);
      const closed = rows.filter((r) => r.status === 'Closed').length;
      const pct =
        rows.length > 0 ? `${Math.round((closed / rows.length) * 100)}%` : '-';
      return [
        k,
        rows.length,
        rows.filter((r) => r.status === 'Open').length,
        rows.filter((r) => r.status === 'In Progress').length,
        closed,
        pct,
      ];
    });

    autoTable(doc, {
      startY: breakdownY + 3,
      head: [
        ['Kategori', 'Jumlah', 'Open', 'In Progress', 'Closed', '% Close'],
      ],
      body: breakdownRows,
      theme: 'striped',
      headStyles: {
        fillColor: [71, 85, 105],
        textColor: 255,
        fontSize: 8,
        fontStyle: 'bold',
        halign: 'center',
      },
      bodyStyles: { fontSize: 9, halign: 'center' },
      columnStyles: { 0: { halign: 'left', fontStyle: 'bold' } },
      margin: { left: 14, right: 14 },
    });

    // Breakdown by department — multi-level header matching reference table
    const deptBreakdownY = doc.lastAutoTable.finalY + 8;
    doc.setTextColor(30, 41, 59);
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    doc.text('BREAKDOWN PER DEPARTEMEN', 14, deptBreakdownY);

    const allDepts = departments.value;
    const headerBg = [200, 210, 220];
    const redBg = [220, 38, 38];
    const amberBg = [217, 119, 6];
    const greenBg = [22, 163, 74];
    const white = [255, 255, 255];
    const dark = [30, 41, 59];

    const catStats = (rows, kat) => ({
      O: rows.filter((r) => r.kategoriTemuan === kat && r.status === 'Open')
        .length,
      I: rows.filter(
        (r) => r.kategoriTemuan === kat && r.status === 'In Progress',
      ).length,
      C: rows.filter((r) => r.kategoriTemuan === kat && r.status === 'Closed')
        .length,
    });

    const deptBodyRows = allDepts.map((dept, idx) => {
      const rows = monthRows.filter((r) => r.departmentId === dept.id);
      const low = catStats(rows, 'Low');
      const med = catStats(rows, 'Medium');
      const high = catStats(rows, 'High');
      const dTotal = rows.length;
      const dClosed = low.C + med.C + high.C;
      const pct = dTotal > 0 ? `${Math.round((dClosed / dTotal) * 100)}%` : '-';
      return [
        idx + 1,
        dept.name.toUpperCase(),
        low.O,
        low.I,
        low.C,
        med.O,
        med.I,
        med.C,
        high.O,
        high.I,
        high.C,
        pct,
      ];
    });

    // Totals row
    const tLow = catStats(monthRows, 'Low');
    const tMed = catStats(monthRows, 'Medium');
    const tHigh = catStats(monthRows, 'High');
    const tAll = monthRows.length;
    const tClosed = tLow.C + tMed.C + tHigh.C;
    const tPct = tAll > 0 ? `${Math.round((tClosed / tAll) * 100)}%` : '-';
    const totalCellStyle = (color) => ({
      styles: { fontStyle: 'bold', textColor: color },
    });
    deptBodyRows.push([
      {
        content: 'TOTAL TEMUAN',
        colSpan: 2,
        styles: {
          fontStyle: 'bold',
          halign: 'center',
          fillColor: [220, 230, 242],
          textColor: dark,
        },
      },
      { content: tLow.O, ...totalCellStyle(redBg) },
      { content: tLow.I, ...totalCellStyle(amberBg) },
      { content: tLow.C, ...totalCellStyle(greenBg) },
      { content: tMed.O, ...totalCellStyle(redBg) },
      { content: tMed.I, ...totalCellStyle(amberBg) },
      { content: tMed.C, ...totalCellStyle(greenBg) },
      { content: tHigh.O, ...totalCellStyle(redBg) },
      { content: tHigh.I, ...totalCellStyle(amberBg) },
      { content: tHigh.C, ...totalCellStyle(greenBg) },
      { content: tPct, styles: { fontStyle: 'bold', textColor: dark } },
    ]);

    const monthLabel = MONTH_NAMES[m - 1].toUpperCase();

    // Column layout (must match columnStyles below)
    const colW = [10, 45, 13, 13, 13, 13, 13, 13, 13, 13, 13, 18];
    const margin = 14;
    const colX = colW.reduce((acc, w, i) => {
      acc.push(i === 0 ? margin : acc[i - 1] + colW[i - 1]);
      return acc;
    }, []);
    const hRowH = 6.5;
    const borderClr = [160, 175, 190];
    let hdrY = deptBreakdownY + 3;

    const fillText = (txt, x, y, w, rh, fill, fg, fs = 7.5) => {
      doc.setFillColor(...fill);
      doc.setDrawColor(...borderClr);
      doc.rect(x, y, w, rh, 'FD');
      if (txt) {
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(fs);
        doc.setTextColor(...fg);
        doc.text(String(txt), x + w / 2, y + rh / 2, {
          align: 'center',
          baseline: 'middle',
        });
      }
    };

    const totalHdrH = hRowH * 3;

    // NO, DEPARTEMEN, % CLOSE — span all 3 rows vertically
    fillText('NO', colX[0], hdrY, colW[0], totalHdrH, headerBg, dark);
    fillText('DEPARTEMEN', colX[1], hdrY, colW[1], totalHdrH, headerBg, dark);
    fillText('% CLOSE', colX[11], hdrY, colW[11], totalHdrH, headerBg, dark);

    // Header row 1 (cols 2-10): MONTH label merged
    fillText(
      monthLabel,
      colX[2],
      hdrY,
      colW.slice(2, 11).reduce((a, b) => a + b, 0),
      hRowH,
      headerBg,
      dark,
    );
    hdrY += hRowH;

    // Header row 2: LOW | MEDIUM | HIGH
    fillText(
      'LOW',
      colX[2],
      hdrY,
      colW.slice(2, 5).reduce((a, b) => a + b, 0),
      hRowH,
      headerBg,
      dark,
    );
    fillText(
      'MEDIUM',
      colX[5],
      hdrY,
      colW.slice(5, 8).reduce((a, b) => a + b, 0),
      hRowH,
      headerBg,
      dark,
    );
    fillText(
      'HIGH',
      colX[8],
      hdrY,
      colW.slice(8, 11).reduce((a, b) => a + b, 0),
      hRowH,
      headerBg,
      dark,
    );
    hdrY += hRowH;

    // Header row 3: O I C repeated
    fillText('O', colX[2], hdrY, colW[2], hRowH, redBg, white);
    fillText('I', colX[3], hdrY, colW[3], hRowH, amberBg, white);
    fillText('C', colX[4], hdrY, colW[4], hRowH, greenBg, white);
    fillText('O', colX[5], hdrY, colW[5], hRowH, redBg, white);
    fillText('I', colX[6], hdrY, colW[6], hRowH, amberBg, white);
    fillText('C', colX[7], hdrY, colW[7], hRowH, greenBg, white);
    fillText('O', colX[8], hdrY, colW[8], hRowH, redBg, white);
    fillText('I', colX[9], hdrY, colW[9], hRowH, amberBg, white);
    fillText('C', colX[10], hdrY, colW[10], hRowH, greenBg, white);
    hdrY += hRowH;

    autoTable(doc, {
      startY: hdrY,
      showHead: 'never',
      body: deptBodyRows,
      theme: 'grid',
      bodyStyles: { fontSize: 8, halign: 'center', textColor: dark },
      columnStyles: {
        0: { cellWidth: colW[0], halign: 'center' },
        1: { cellWidth: colW[1], halign: 'left', fontStyle: 'bold' },
        2: { cellWidth: colW[2] },
        3: { cellWidth: colW[3] },
        4: { cellWidth: colW[4] },
        5: { cellWidth: colW[5] },
        6: { cellWidth: colW[6] },
        7: { cellWidth: colW[7] },
        8: { cellWidth: colW[8] },
        9: { cellWidth: colW[9] },
        10: { cellWidth: colW[10] },
        11: { cellWidth: colW[11] },
      },
      margin: { left: margin, right: margin },
    });

    // Detail findings
    const detailY = doc.lastAutoTable.finalY + 8;
    doc.setTextColor(30, 41, 59);
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    doc.text('DETAIL TEMUAN', 14, detailY);

    if (monthRows.length === 0) {
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(9);
      doc.setTextColor(148, 163, 184);
      doc.text(
        `Tidak ada data temuan untuk ${MONTH_NAMES[m - 1]} ${y}.`,
        14,
        detailY + 6,
      );
    } else {
      autoTable(doc, {
        startY: detailY + 3,
        head: [
          [
            'No',
            'Tanggal',
            'Kategori',
            'Deskripsi Temuan',
            'Lokasi',
            'Tindakan Perbaikan',
            'Target',
            'Status',
            'Aktual Close',
          ],
        ],
        body: monthRows.map((r, i) => {
          const isOvd =
            r.status !== 'Closed' &&
            r.targetSelesai &&
            new Date(r.targetSelesai) < todayDate;
          return [
            i + 1,
            fmtDate(r.tanggal),
            r.kategoriTemuan || '-',
            r.deskripsiTemuan || '-',
            r.lokasi || '-',
            r.tindakanPerbaikan || '-',
            fmtDate(r.targetSelesai),
            r.status || '-',
            fmtDate(r.aktualClose),
          ];
        }),
        theme: 'striped',
        headStyles: {
          fillColor: [71, 85, 105],
          textColor: 255,
          fontSize: 7.5,
          fontStyle: 'bold',
        },
        bodyStyles: { fontSize: 8, textColor: [51, 65, 85] },
        columnStyles: {
          0: { cellWidth: 8, halign: 'center' },
          1: { cellWidth: 22 },
          2: { cellWidth: 18, halign: 'center' },
          3: { cellWidth: 'auto', minCellWidth: 35 },
          4: { cellWidth: 25 },
          5: { cellWidth: 'auto', minCellWidth: 35 },
          6: { cellWidth: 22 },
          7: { cellWidth: 22, halign: 'center' },
          8: { cellWidth: 22 },
        },
        didParseCell(data) {
          if (data.section === 'body') {
            const row = monthRows[data.row.index];
            const isOvd =
              row &&
              row.status !== 'Closed' &&
              row.targetSelesai &&
              new Date(row.targetSelesai) < todayDate;
            if (isOvd) data.cell.styles.textColor = [220, 38, 38];
            if (row && row.status === 'Closed')
              data.cell.styles.textColor = [148, 163, 184];
          }
        },
        margin: { left: 14, right: 14 },
      });
    }

    // Footer on each page
    const pageCount = doc.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
      doc.setPage(i);
      doc.setFontSize(7);
      doc.setTextColor(148, 163, 184);
      doc.text(
        `Halaman ${i} dari ${pageCount}`,
        pageW / 2,
        doc.internal.pageSize.getHeight() - 6,
        { align: 'center' },
      );
    }

    doc.save(`laporan-k3l-${y}-${String(m).padStart(2, '0')}.pdf`);
    if (closeModal) showExportModal.value = false;
  } finally {
    pdfGenerating.value = false;
  }
}

onBeforeUnmount(() => {
  destroyCharts();
});

onMounted(async () => {
  await loadData(true);
  await loadLocationOptions();
  if (roleLevel >= 3 && roleLevel < 5) {
    availablePlants.value = await inspectionK3LService.listPlants(
      currentUser?.businessUnitId,
    );
  } else {
    availablePlants.value = plants.value;
  }
  if (route.query.view) {
    const target = records.value.find(
      (r) => String(r.id) === String(route.query.view),
    );
    if (target) viewRecord(target);
  }
});
</script>

<style scoped>
.inspection-k3l {
  padding: 28px 32px;
  max-width: 1400px;
  overflow-x: hidden;
}
@media (max-width: 1024px) {
  .inspection-k3l {
    padding: 20px 20px;
  }
}
@media (max-width: 640px) {
  .inspection-k3l {
    padding: 16px 14px;
  }
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 8px;
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
  .page-header .btn-primary {
    width: 100%;
    justify-content: center;
  }
}

/* ── Action bar ── */
.action-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 10px;
}

/* ── Scope filter (inline beside action bar) ── */
.scope-filter-inline {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  flex-basis: 100%;
  min-width: 0;
}
.scope-select {
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background: #fff;
  color: #1e293b;
  font-size: 13px;
  padding: 6px 10px;
  outline: none;
  cursor: pointer;
  transition: border-color 0.15s;
  /* truncate long option text */
  max-width: 180px;
  min-width: 0;
  text-overflow: ellipsis;
  overflow: hidden;
}
.scope-select:focus {
  border-color: #3b82f6;
}
.scope-bu-label {
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 6px 12px;
  white-space: nowrap;
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
}
.scope-reset-btn {
  font-size: 13px;
  color: #ef4444;
  background: transparent;
  border: 1px solid #ef4444;
  border-radius: 8px;
  padding: 6px 12px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s;
}
.scope-reset-btn:hover {
  background: #fef2f2;
}
@media (max-width: 640px) {
  .scope-select {
    max-width: 140px;
    flex: 1;
  }
}

/* ── Buttons ── */
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
  background: #f1f5f9;
  border: none;
  cursor: pointer;
  padding: 6px;
  border-radius: 7px;
  color: #64748b;
  display: inline-flex;
  align-items: center;
  gap: 3px;
  transition:
    background 0.15s,
    color 0.15s;
  position: relative;
}
.btn-icon:hover {
  background: #e2e8f0;
  color: #3b82f6;
}
.btn-danger {
  background: #fef2f2;
  color: #ef4444;
}
.btn-danger:hover {
  background: #fee2e2;
  color: #dc2626;
}
.btn-eye {
  background: #faf5ff;
  color: #9333ea;
}
.btn-eye:hover {
  background: #f3e8ff;
  color: #7e22ce;
}
.btn-eye-after {
  background: #f0fdf4;
  color: #16a34a;
}
.btn-eye-after:hover {
  background: #dcfce7;
  color: #15803d;
}

.photo-count-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  font-size: 9px;
  font-weight: 700;
  background: #9333ea;
  color: #fff;
  border-radius: 999px;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}
.photo-count-badge-after {
  background: #16a34a;
}

.text-muted {
  color: #cbd5e1;
  font-size: 13px;
}

/* ── Modals ── */
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

/* ── Detail view layout ── */
.detail-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.detail-section {
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 16px;
}
.detail-section:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.detail-row {
  display: flex;
  gap: 12px;
  padding: 6px 0;
  border-bottom: 1px solid #f8fafc;
}
.detail-row:last-child {
  border-bottom: none;
}

.detail-label {
  font-size: 13px;
  font-weight: 600;
  color: #94a3b8;
  min-width: 150px;
  flex-shrink: 0;
}

.detail-value {
  font-size: 14px;
  color: #1e293b;
  flex: 1;
}

.detail-multiline {
  white-space: pre-wrap;
  line-height: 1.6;
}

.detail-photo-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 8px;
}

.detail-photo-thumb {
  width: 90px;
  height: 90px;
  object-fit: cover;
  border-radius: 8px;
  border: 2px solid #e2e8f0;
  cursor: pointer;
  transition:
    border-color 0.15s,
    transform 0.15s;
}
.detail-photo-thumb:hover {
  border-color: #9333ea;
  transform: scale(1.04);
}

/* ── Lightbox ── */
.lightbox-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.92);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.lightbox-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: 90vw;
  max-height: 90vh;
}

.lightbox-img {
  max-width: 100%;
  max-height: 80vh;
  object-fit: contain;
  border-radius: 8px;
}

.lightbox-dots {
  position: absolute;
  bottom: 24px;
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

.lightbox-close {
  position: absolute;
  top: 20px;
  right: 20px;
  background: rgba(255, 255, 255, 0.15);
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
}
.lightbox-close:hover {
  background: rgba(255, 255, 255, 0.25);
}

.lightbox-nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255, 255, 255, 0.15);
  border: none;
  border-radius: 50%;
  width: 44px;
  height: 44px;
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
}
.lightbox-nav:hover {
  background: rgba(255, 255, 255, 0.28);
}
.lightbox-prev {
  left: 20px;
}
.lightbox-next {
  right: 20px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
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
.form-group-fill {
  max-width: none;
  flex: 1;
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
  padding: 9px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  color: #1e293b;
  background: #fff;
  transition:
    border-color 0.15s,
    box-shadow 0.15s;
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
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.12);
}
.form-group textarea {
  resize: vertical;
}

.date-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}
.date-input-wrapper input {
  width: 100%;
  padding-right: 36px;
  cursor: pointer;
  color-scheme: light;
}
.date-input-wrapper input::-webkit-calendar-picker-indicator {
  opacity: 0;
  position: absolute;
  right: 0;
  width: 36px;
  height: 100%;
  cursor: pointer;
}
.date-icon {
  position: absolute;
  right: 10px;
  color: #475569;
  cursor: pointer;
  transition: color 0.15s;
  pointer-events: none;
}
.date-icon:hover {
  color: #3b82f6;
}

.photo-count {
  font-weight: 400;
  color: #94a3b8;
  font-size: 12px;
}
.photo-readonly-tag {
  font-weight: 400;
  font-size: 11px;
  color: #fff;
  background: #94a3b8;
  border-radius: 4px;
  padding: 1px 6px;
  margin-left: 6px;
  vertical-align: middle;
}
.photo-readonly-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 12px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}
.photo-readonly-thumb {
  width: 100px;
  height: 100px;
  border-radius: 8px;
  object-fit: cover;
  border: 1px solid #e2e8f0;
  cursor: zoom-in;
  transition: opacity 0.15s;
}
.photo-readonly-thumb:hover {
  opacity: 0.85;
}
.photo-empty {
  padding: 16px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  color: #94a3b8;
  font-size: 13px;
  text-align: center;
}
.foto-sublabel {
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  margin: 0 0 8px;
  text-transform: uppercase;
  letter-spacing: 0.4px;
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
}

.photo-clear {
  margin-top: 8px;
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

.form-actions {
  display: flex;
  gap: 12px;
  padding-top: 8px;
}

.field-auto-tag {
  font-size: 10px;
  font-weight: 600;
  color: #fff;
  background: #64748b;
  border-radius: 4px;
  padding: 1px 5px;
  margin-left: 5px;
  vertical-align: middle;
  letter-spacing: 0.2px;
}

.field-auto {
  background: #f1f5f9 !important;
  color: #64748b !important;
  cursor: not-allowed !important;
  border-color: #e2e8f0 !important;
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
.toast-enter-from {
  opacity: 0;
  transform: translateX(40px);
}
.toast-leave-to {
  opacity: 0;
  transform: translateX(40px);
}

/* ── Table ── */
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

.table-header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.btn-export {
  display: flex;
  align-items: center;
  gap: 5px;
  background: #f0fdf4;
  color: #166534;
  border-color: #bbf7d0;
}

.btn-export:hover:not(:disabled) {
  background: #dcfce7;
  border-color: #86efac;
}

.btn-export:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ── Date filter row ── */
.date-filter-row {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px 6px;
  flex-wrap: nowrap;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}
.date-filter-row::-webkit-scrollbar {
  display: none;
}
.custom-date-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 16px 10px;
  flex-wrap: wrap;
  border-bottom: 1px solid #f1f5f9;
}
.date-chip {
  background: #f1f5f9;
  border: 1px solid transparent;
  border-radius: 20px;
  padding: 5px 14px;
  font-size: 13px;
  color: #64748b;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
  flex-shrink: 0;
}
.date-chip:hover {
  background: #e2e8f0;
  color: #1e293b;
}
.date-chip.active {
  background: #3b82f6;
  color: #fff;
  border-color: #3b82f6;
}
.toolbar-date-wrap {
  display: inline-flex;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background: #fff;
  overflow: hidden;
  cursor: pointer;
  transition: border-color 0.15s;
}
.toolbar-date-wrap:focus-within {
  border-color: #3b82f6;
}
.toolbar-date {
  border: none;
  background: transparent;
  color: #1e293b;
  font-size: 13px;
  padding: 6px 10px;
  outline: none;
  cursor: pointer;
  color-scheme: light;
  width: 140px;
}
.date-sep {
  color: #94a3b8;
  font-size: 13px;
}

/* ── Filter bar ── */
.filter-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  border-bottom: 1px solid #f1f5f9;
  flex-wrap: nowrap;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}

.filter-bar::-webkit-scrollbar {
  display: none;
}

.search-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  flex-shrink: 0;
  width: 200px;
}

.search-icon {
  position: absolute;
  left: 10px;
  color: #94a3b8;
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 7px 32px 7px 32px;
  border: 1px solid #e2e8f0;
  border-radius: 7px;
  font-size: 13px;
  color: #1e293b;
  background: #f8fafc;
  outline: none;
  transition:
    border-color 0.15s,
    background 0.15s;
}

.search-input:focus {
  border-color: #3b82f6;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.08);
}

.search-clear {
  position: absolute;
  right: 8px;
  background: none;
  border: none;
  cursor: pointer;
  color: #94a3b8;
  font-size: 17px;
  line-height: 1;
  padding: 2px 4px;
  border-radius: 4px;
  transition: color 0.15s;
}
.search-clear:hover {
  color: #475569;
}

.filter-select {
  padding: 7px 10px;
  border: 1px solid #e2e8f0;
  border-radius: 7px;
  font-size: 13px;
  color: #475569;
  background: #f8fafc;
  cursor: pointer;
  outline: none;
  transition: border-color 0.15s;
  flex-shrink: 0;
  white-space: nowrap;
}
.filter-select:focus {
  border-color: #3b82f6;
}

.btn-reset-filters {
  padding: 6px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 7px;
  font-size: 12px;
  font-weight: 600;
  background: #fff;
  color: #64748b;
  cursor: pointer;
  white-space: nowrap;
  transition:
    background 0.15s,
    color 0.15s;
}
.btn-reset-filters:hover {
  background: #f1f5f9;
  color: #334155;
}

.filter-count {
  font-size: 12px;
  color: #94a3b8;
  white-space: nowrap;
}

.btn-inline-link {
  background: none;
  border: none;
  color: #3b82f6;
  cursor: pointer;
  font-size: inherit;
  padding: 0;
  text-decoration: underline;
}

.table-wrapper {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1100px;
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
  padding: 11px 14px;
  font-size: 13px;
  color: #334155;
  border-top: 1px solid #f1f5f9;
  vertical-align: middle;
}

.td-nowrap {
  white-space: nowrap;
}
.td-center {
  text-align: center;
}

.td-truncate {
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.td-actions {
  white-space: nowrap;
  vertical-align: middle;
}
.td-actions .actions-wrap {
  display: flex;
  gap: 2px;
  align-items: center;
  justify-content: center;
}

tbody tr:hover {
  background: #f8fafc;
}

tbody tr.row-clickable {
  cursor: pointer;
}

/* ── Badges ── */
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

.kategori-badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}
.kategori-low {
  background: #f0fdf4;
  color: #16a34a;
  border: 1px solid #bbf7d0;
}
.kategori-medium {
  background: #fffbeb;
  color: #b45309;
  border: 1px solid #fde68a;
}
.kategori-high {
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

.comment-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 9px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  background: #f1f5f9;
  color: #94a3b8;
  border: 1px solid #e2e8f0;
}
.comment-badge.has-comments {
  background: #eff6ff;
  color: #1d4ed8;
  border-color: #bfdbfe;
}
.detail-comments {
  grid-column: 1 / -1;
  margin-top: 6px;
}

/* ── Empty state ── */
.empty-state {
  padding: 40px 20px;
  text-align: center;
  color: #94a3b8;
  font-size: 14px;
}

/* ── Discard confirm ── */
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

/* ── Mobile responsive ── */
@media (max-width: 640px) {
  .inspection-k3l {
    padding: 16px;
  }

  /* Table stays as table — horizontal scroll only */
  .table-wrapper {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    border-radius: 0 0 8px 8px;
  }

  table {
    min-width: 1000px;
  }

  .table-card {
    border-radius: 8px;
  }

  .modal-overlay {
    padding: 12px;
  }
  .modal-container {
    border-radius: 14px;
    max-height: 92vh;
    max-width: 100%;
  }
  .modal-header {
    padding: 16px 16px 12px;
  }
  .modal-body {
    padding: 16px;
  }

  .form-row {
    flex-direction: column;
    gap: 12px;
  }
  .form-group {
    min-width: 0;
    max-width: 100%;
    flex: 1 1 100%;
  }
  .form-group-fill {
    max-width: 100%;
  }

  .photo-actions {
    flex-direction: row;
    gap: 8px;
  }
  .photo-btn {
    flex: 1;
    padding: 10px 8px;
    font-size: 12px;
  }
  .photo-preview img {
    width: 80px;
    height: 80px;
  }

  .form-actions {
    flex-direction: column;
  }
  .form-actions .btn {
    width: 100%;
    text-align: center;
  }

  .detail-label {
    min-width: 110px;
  }

  .toast {
    top: auto;
    bottom: 16px;
    right: 12px;
    left: 12px;
    max-width: 100%;
  }

  .lightbox-prev {
    left: 8px;
  }
  .lightbox-next {
    right: 8px;
  }
}

@media (min-width: 641px) and (max-width: 1024px) {
  .inspection-k3l {
    padding: 20px;
  }
  table {
    min-width: 1000px;
  }
}

/* ── Monthly Report Buttons ─────────────────────────────────────────────── */

.btn-summary {
  background: #eff6ff;
  color: #2563eb;
  border: 1px solid #bfdbfe;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}
.btn-summary:hover {
  background: #dbeafe;
  border-color: #93c5fd;
}

.btn-print-report {
  background: #faf5ff;
  color: #7c3aed;
  border: 1px solid #ddd6fe;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}
.btn-print-report:hover {
  background: #ede9fe;
  border-color: #c4b5fd;
}

/* ── Monthly modals shared container overrides ──────────────────────────── */
.modal-export-monthly {
  max-width: 420px;
}
.modal-summary {
  max-width: 720px;
  width: 92vw;
}

/* Modal desc text */
.modal-desc {
  font-size: 13px;
  color: #475569;
  margin: 0 0 18px;
  line-height: 1.5;
}

.export-preview-text {
  margin-top: 4px;
  font-size: 13px;
  color: #374151;
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: var(--r-md);
  padding: 9px 14px;
}

/* Footer bar for the new modals */
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
.export-btn-group {
  display: flex;
  gap: 8px;
}
.btn-export-csv {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 8px 16px;
  background: #f0fdf4;
  color: #15803d;
  border: 1.5px solid #86efac;
  border-radius: 7px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition:
    background 0.15s,
    border-color 0.15s;
}
.btn-export-csv:hover {
  background: #dcfce7;
  border-color: #4ade80;
}
.btn-export-pdf {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 8px 16px;
  background: #7c3aed;
  color: #fff;
  border: 1.5px solid #7c3aed;
  border-radius: 7px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-export-pdf:hover:not(:disabled) {
  background: #6d28d9;
  border-color: #6d28d9;
}
.btn-export-pdf:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* ── Monthly Summary Modal ──────────────────────────────────────────────── */
.summary-month-row {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}
.kpi-row {
  display: flex;
  gap: 10px;
  margin-bottom: 22px;
  flex-wrap: wrap;
}
.kpi-card {
  flex: 1;
  min-width: 88px;
  border-radius: 10px;
  padding: 14px 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  border: 1.5px solid transparent;
}
.kpi-value {
  font-size: 30px;
  font-weight: 800;
  line-height: 1;
}
.kpi-label {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.6px;
}
.kpi-total {
  background: #f1f5f9;
  color: #1e293b;
  border-color: #cbd5e1;
}
.kpi-open {
  background: #fef2f2;
  color: #dc2626;
  border-color: #fca5a5;
}
.kpi-inprogress {
  background: #fffbeb;
  color: #b45309;
  border-color: #fcd34d;
}
.kpi-closed {
  background: #f0fdf4;
  color: #15803d;
  border-color: #86efac;
}
.kpi-overdue {
  background: #faf5ff;
  color: #7c3aed;
  border-color: #d8b4fe;
}

.charts-row {
  display: flex;
  gap: 14px;
}
.chart-wrap {
  flex: 1;
  min-width: 0;
  background: #fff;
  border: 1.5px solid #e2e8f0;
  border-radius: 10px;
  padding: 14px 12px 10px;
}
.chart-title {
  font-size: 12px;
  font-weight: 700;
  color: #374151;
  margin: 0 0 10px;
  text-align: center;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}
</style>
