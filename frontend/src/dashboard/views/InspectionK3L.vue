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
      <button class="btn btn-primary" @click="showForm = true">
        + Tambah Temuan
      </button>
    </div>

    <!-- ── Input / Edit Form Modal ── -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showForm" class="modal-overlay" @click.self="tryCloseForm">
          <div class="modal-container">
            <div class="modal-header">
              <h3 class="modal-title">
                {{ editingId ? 'Edit Temuan' : 'Input Temuan Baru' }}
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
                                style="display:none"
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
                                style="display:none"
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
                                style="display:none"
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
                                style="display:none"
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
                      <label>Business Unit <span class="field-auto-tag">Otomatis</span></label>
                      <input
                        type="text"
                        :value="getBusinessUnitName(form.businessUnitId)"
                        disabled
                        class="field-auto"
                        placeholder="-"
                      />
                    </div>
                    <div class="form-group form-group-fill">
                      <label>Plant <span class="field-auto-tag">Otomatis</span></label>
                      <input
                        type="text"
                        :value="getPlantName(form.plantId)"
                        disabled
                        class="field-auto"
                        placeholder="-"
                      />
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
                  </div>
                </div>

                <!-- Submit -->
                <div class="form-actions">
                  <button
                    type="submit"
                    class="btn btn-primary"
                    :disabled="submitting"
                  >
                    {{
                      submitting
                        ? 'Menyimpan...'
                        : editingId
                          ? 'Update'
                          : 'Simpan'
                    }}
                  </button>
                  <button
                    type="button"
                    class="btn btn-secondary"
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
                      formatDate(viewingRecord.targetSelesai)
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
          @keydown.left="photoModalIndex = (photoModalIndex - 1 + photoModalImages.length) % photoModalImages.length"
          @keydown.right="photoModalIndex = (photoModalIndex + 1) % photoModalImages.length"
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
            <span v-for="(_, i) in photoModalImages" :key="i" class="lightbox-dot" :class="{ active: i === photoModalIndex }" @click.stop="photoModalIndex = i"></span>
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
                  class="btn btn-secondary"
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
        <div v-if="showDiscardConfirm" class="modal-overlay" style="z-index:1100">
          <div class="modal-container modal-sm">
            <div class="modal-body" style="padding:28px 24px 20px">
              <div class="discard-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="36" height="36">
                  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                  <line x1="12" y1="9" x2="12" y2="13"/>
                  <line x1="12" y1="17" x2="12.01" y2="17"/>
                </svg>
              </div>
              <h4 class="discard-title">Batalkan perubahan?</h4>
              <p class="discard-desc">Anda memiliki data yang belum disimpan. Apakah yakin ingin menutup form ini?</p>
            </div>
            <div class="discard-footer">
              <button class="btn btn-secondary" @click="showDiscardConfirm = false">Kembali</button>
              <button class="btn btn-discard-confirm" @click="forceCloseForm">Ya, Batalkan</button>
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
          <button
            class="btn btn-sm btn-export"
            @click="exportCsv"
            :disabled="filteredRecords.length === 0"
            title="Export semua data ke CSV"
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
            Export CSV
          </button>
          <button class="btn btn-sm" @click="loadData" :disabled="loading">
            {{ loading ? 'Loading...' : 'Refresh' }}
          </button>
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

      <!-- Filter bar -->
      <div class="filter-bar">
        <div class="search-wrapper">
          <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15">
            <circle cx="11" cy="11" r="8"/>
            <line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input
            type="text"
            v-model="searchQuery"
            class="search-input"
            placeholder="Cari deskripsi, lokasi, tanggal..."
          />
          <button v-if="searchQuery" class="search-clear" @click="searchQuery = ''">&times;</button>
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

        <button v-if="hasActiveFilters" class="btn-reset-filters" @click="resetFilters">
          Reset
        </button>

        <span v-if="hasActiveFilters" class="filter-count">
          {{ filteredRecords.length }} / {{ records.length }} data
        </span>
      </div>

      <div class="table-wrapper">
        <table v-if="filteredRecords.length > 0">
          <thead>
            <tr>
              <th>No</th>
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
              <th>Status</th>
              <th>Aksi</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, idx) in filteredRecords" :key="item.id">
              <td>{{ idx + 1 }}</td>
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
              <td class="td-center">
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
              <td class="td-center">
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
              <td class="td-nowrap">{{ getDepartmentName(item.departmentId) }}</td>
              <td class="td-nowrap">
                {{ getBusinessUnitName(item.businessUnitId) }}
              </td>
              <td class="td-nowrap">{{ getPlantName(item.plantId) }}</td>
              <td class="td-truncate">{{ item.tindakanPerbaikan || '-' }}</td>
              <td class="td-nowrap">{{ formatDate(item.targetSelesai) }}</td>
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
              <td class="td-actions">
                <button
                  class="btn-icon btn-view"
                  title="Lihat Detail"
                  @click="viewRecord(item)"
                >
                  <svg
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    width="16"
                    height="16"
                  >
                    <circle cx="11" cy="11" r="8" />
                    <line x1="21" y1="21" x2="16.65" y2="16.65" />
                    <line x1="11" y1="8" x2="11" y2="14" />
                    <line x1="8" y1="11" x2="14" y2="11" />
                  </svg>
                </button>
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
              </td>
            </tr>
          </tbody>
        </table>
        <div v-else-if="hasActiveFilters" class="empty-state">
          <p>Tidak ada data yang cocok dengan filter. <button class="btn-inline-link" @click="resetFilters">Reset filter</button></p>
        </div>
        <div v-else class="empty-state">
          <p>Belum ada data temuan. Klik "Tambah Temuan" untuk menambahkan.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import {
  inspectionK3LService,
  uploadImage,
} from '@/services/inspectionK3LService.js';
import { exportToCsv } from '@/services/exportCsvService.js';
import { authService } from '@/services/authService.js';

const currentUser = authService.getCurrentUser();

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
  if (val !== 'custom') { customDateFrom.value = ''; customDateTo.value = ''; }
}

const hasActiveFilters = computed(
  () => searchQuery.value.trim() !== '' || filterKategori.value !== '' || filterStatus.value !== '' || filterDate.value !== 'all',
);

const filteredRecords = computed(() => {
  let result = records.value;

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
    const today = new Date(); today.setHours(0, 0, 0, 0);
    result = result.filter((r) => {
      if (!r.tanggal) return false;
      const d = new Date(r.tanggal); d.setHours(0, 0, 0, 0);
      if (filterDate.value === 'today') return d.getTime() === today.getTime();
      if (filterDate.value === 'week') {
        const start = new Date(today); start.setDate(today.getDate() - today.getDay());
        const end = new Date(start); end.setDate(start.getDate() + 6);
        return d >= start && d <= end;
      }
      if (filterDate.value === 'month') return d.getMonth() === today.getMonth() && d.getFullYear() === today.getFullYear();
      if (filterDate.value === 'custom') {
        if (customDateFrom.value) { const from = new Date(customDateFrom.value); from.setHours(0,0,0,0); if (d < from) return false; }
        if (customDateTo.value)   { const to   = new Date(customDateTo.value);   to.setHours(0,0,0,0);   if (d > to)   return false; }
      }
      return true;
    });
  }

  return result;
});

function resetFilters() {
  searchQuery.value = '';
  filterKategori.value = '';
  filterStatus.value = '';
  filterDate.value = 'all';
  customDateFrom.value = '';
  customDateTo.value = '';
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
  const [y, m, d] = val.split('-');
  if (!y || !m || !d) return val;
  return `${d}/${m}/${y}`;
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

function hasFormChanges() {
  if (!editingId.value) {
    const f = form.value;
    return !!(
      f.tanggal || f.kategoriTemuan || f.deskripsiTemuan || f.lokasi ||
      f.tindakanPerbaikan || f.targetSelesai || f.businessUnitId ||
      f.plantId || f.departmentId || photos.value.length > 0
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
    console.error("[InspectionK3L] loadData:", e);
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
    console.error("[InspectionK3L] loadLocationOptions:", e);
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
      aktualClose: form.value.aktualClose || null,
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
    console.error("[InspectionK3L] submitForm:", e);
  } finally {
    submitting.value = false;
  }
}

function editRecord(item) {
  editingId.value = item.id;
  const formValues = {
    tanggal: item.tanggal,
    kategoriTemuan: item.kategoriTemuan,
    deskripsiTemuan: item.deskripsiTemuan || '',
    lokasi: item.lokasi || '',
    tindakanPerbaikan: item.tindakanPerbaikan || '',
    targetSelesai: item.targetSelesai || '',
    status: item.status,
    aktualClose: item.aktualClose || '',
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
    console.error("[InspectionK3L] confirmDelete:", e);
  } finally {
    deleting.value = false;
  }
}

function exportCsv() {
  const source = filteredRecords.value;
  // Parse all photo URL arrays upfront to determine column count
  const parsedPhotos = source.map((row) => {
    if (!row.fotoSebelum) return [];
    try {
      const parsed = JSON.parse(row.fotoSebelum);
      return Array.isArray(parsed) ? parsed : [row.fotoSebelum];
    } catch {
      return [row.fotoSebelum];
    }
  });

  const maxPhotos = parsedPhotos.reduce((max, p) => Math.max(max, p.length), 0);

  const rows = source.map((row, idx) => {
    const photos = parsedPhotos[idx];
    const photoFields = {};
    for (let i = 0; i < maxPhotos; i++) {
      // =IMAGE("url") renders the image inline in Excel 365
      photoFields[`foto_${i + 1}`] = photos[i] ? `=IMAGE("${photos[i]}")` : '';
    }
    return {
      no: idx + 1,
      tanggal: row.tanggal || '',
      kategoriTemuan: row.kategoriTemuan || '',
      deskripsiTemuan: row.deskripsiTemuan || '',
      lokasi: row.lokasi || '',
      tindakanPerbaikan: row.tindakanPerbaikan || '',
      targetSelesai: row.targetSelesai || '',
      status: row.status || '',
      aktualClose: row.aktualClose || '',
      ...photoFields,
    };
  });

  const photoColumnDefs = Array.from({ length: maxPhotos }, (_, i) => ({
    label: `Foto ${i + 1}`,
    key: `foto_${i + 1}`,
    formula: true,
  }));

  const columns = [
    { label: 'No', key: 'no' },
    { label: 'Tanggal', key: 'tanggal' },
    { label: 'Kategori Temuan', key: 'kategoriTemuan' },
    { label: 'Deskripsi Temuan', key: 'deskripsiTemuan' },
    { label: 'Lokasi', key: 'lokasi' },
    { label: 'Tindakan Perbaikan', key: 'tindakanPerbaikan' },
    { label: 'Target Selesai', key: 'targetSelesai' },
    { label: 'Status', key: 'status' },
    { label: 'Aktual Close', key: 'aktualClose' },
    ...photoColumnDefs,
  ];

  const today = new Date().toISOString().slice(0, 10);
  exportToCsv(`inspection-k3l-${today}.csv`, columns, rows);
}

onMounted(async () => {
  await loadData(true);
  loadLocationOptions(true);
  if (route.query.view) {
    const target = records.value.find(r => String(r.id) === String(route.query.view));
    if (target) viewRecord(target);
  }
});
</script>

<style scoped>
.inspection-k3l {
  padding: 32px;
  max-width: 1400px;
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

.action-bar {
  margin-bottom: 16px;
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
  background: none;
  border: none;
  cursor: pointer;
  padding: 5px;
  border-radius: 5px;
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
  background: #f1f5f9;
  color: #3b82f6;
}
.btn-danger:hover {
  background: #fef2f2;
  color: #ef4444;
}
.btn-view:hover {
  background: #f0f9ff;
  color: #0284c7;
}
.btn-eye:hover {
  background: #fdf4ff;
  color: #9333ea;
}
.btn-eye-after {
  color: #16a34a;
}
.btn-eye-after:hover {
  background: #f0fdf4;
  color: #16a34a;
}

.photo-count-badge {
  font-size: 10px;
  font-weight: 700;
  background: #9333ea;
  color: #fff;
  border-radius: 8px;
  padding: 1px 5px;
  line-height: 1.4;
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
  background: rgba(15, 23, 42, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 16px;
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
.date-filter-row { display: flex; align-items: center; gap: 6px; padding: 10px 16px; border-bottom: 1px solid #f1f5f9; flex-wrap: wrap; }
.date-chip { background: #f1f5f9; border: 1px solid transparent; border-radius: 20px; padding: 5px 14px; font-size: 13px; color: #64748b; cursor: pointer; transition: all 0.15s; white-space: nowrap; }
.date-chip:hover { background: #e2e8f0; color: #1e293b; }
.date-chip.active { background: #3b82f6; color: #fff; border-color: #3b82f6; }
.toolbar-date-wrap { display: inline-flex; border: 1px solid #cbd5e1; border-radius: 8px; background: #fff; overflow: hidden; cursor: pointer; transition: border-color 0.15s; }
.toolbar-date-wrap:focus-within { border-color: #3b82f6; }
.toolbar-date { border: none; background: transparent; color: #1e293b; font-size: 13px; padding: 6px 10px; outline: none; cursor: pointer; color-scheme: light; width: 140px; }
.date-sep { color: #94a3b8; font-size: 13px; }

/* ── Filter bar ── */
.filter-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  border-bottom: 1px solid #f1f5f9;
  flex-wrap: wrap;
}

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
  padding: 7px 32px 7px 32px;
  border: 1px solid #e2e8f0;
  border-radius: 7px;
  font-size: 13px;
  color: #1e293b;
  background: #f8fafc;
  outline: none;
  transition: border-color 0.15s, background 0.15s;
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
.search-clear:hover { color: #475569; }

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
}
.filter-select:focus { border-color: #3b82f6; }

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
  transition: background 0.15s, color 0.15s;
}
.btn-reset-filters:hover { background: #f1f5f9; color: #334155; }

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
  display: flex;
  gap: 2px;
  align-items: center;
}

tbody tr:hover {
  background: #f8fafc;
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
.kategori-low { background: #f0fdf4; color: #16a34a; border: 1px solid #bbf7d0; }
.kategori-medium { background: #fffbeb; color: #b45309; border: 1px solid #fde68a; }
.kategori-high { background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; }

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
.btn-discard-confirm:hover { background: #dc2626; }

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
</style>
