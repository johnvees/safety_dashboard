<template>
  <div class="master-data">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h2 class="page-title">Master Data</h2>
        <p class="page-sub">Kelola data Business Unit, Plant, User, dan Department</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'bu' }"
        @click="activeTab = 'bu'"
      >
        Business Unit
      </button>
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'plant' }"
        @click="activeTab = 'plant'"
      >
        Plant
      </button>
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'dept' }"
        @click="activeTab = 'dept'"
      >
        Department
      </button>
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'role' }"
        @click="activeTab = 'role'"
      >
        Peran
      </button>
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'user' }"
        @click="activeTab = 'user'"
      >
        Pengguna
      </button>
    </div>

    <!-- ── Business Unit Tab ───────────────────────────────────────── -->
    <div v-if="activeTab === 'bu'">
      <div class="section-bar">
        <div class="filter-group">
          <span class="total-badge">{{ filteredBu.length }} data</span>
          <div class="search-box">
            <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <input v-model="buSearch" type="text" placeholder="Cari nama atau kode…" class="search-input" />
            <button v-if="buSearch" class="search-clear" @click="buSearch = ''">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
        </div>
        <button class="btn-primary" @click="openBuForm()">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon-inline">
            <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          Tambah Business Unit
        </button>
      </div>

      <div class="card">
        <div class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>No</th>
                <th>Nama</th>
                <th>Kode</th>
                <th>Deskripsi</th>
                <th>Status</th>
                <th>Dibuat</th>
                <th class="th-action">Aksi</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="buLoading">
                <td colspan="7" class="td-empty td-loading">
                  <div class="spinner"></div>
                  <span>Memuat data…</span>
                </td>
              </tr>
              <tr v-else-if="!filteredBu.length">
                <td colspan="7" class="td-empty">
                  {{ buSearch ? 'Tidak ada hasil untuk "' + buSearch + '"' : 'Belum ada data Business Unit' }}
                </td>
              </tr>
              <tr v-for="(item, idx) in pagedBu" :key="item.id">
                <td class="td-num">{{ (buPage - 1) * buPer + idx + 1 }}</td>
                <td class="td-name">{{ item.name }}</td>
                <td><span class="code-badge">{{ item.code }}</span></td>
                <td class="td-desc">{{ item.description || '-' }}</td>
                <td>
                  <span :class="['status-pill', item.isActive ? 'pill-active' : 'pill-inactive']">
                    {{ item.isActive ? 'Aktif' : 'Nonaktif' }}
                  </span>
                </td>
                <td class="td-date">{{ formatDate(item.createdAt) }}</td>
                <td class="td-action">
                  <button class="btn-icon btn-edit" title="Ubah" @click="openBuForm(item)">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                    </svg>
                  </button>
                  <button class="btn-icon btn-danger" title="Hapus" @click="confirmDeleteBu(item)">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                      <polyline points="3 6 5 6 21 6"/>
                      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                    </svg>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
          <PaginationBar :current-page="buPage" :total-pages="buPages" :total-items="buTotal" :per-page="buPer" @page="buGo" @per-page="buSetPer" />
        </div>
      </div>
    </div>

    <!-- ── Plant Tab ──────────────────────────────────────────────── -->
    <div v-if="activeTab === 'plant'">
      <div class="section-bar">
        <div class="filter-group">
          <span class="total-badge">{{ filteredPlants.length }} data</span>
          <div class="search-box">
            <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <input v-model="plantSearch" type="text" placeholder="Cari nama atau kode…" class="search-input" />
            <button v-if="plantSearch" class="search-clear" @click="plantSearch = ''">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
          <select v-model="plantFilterBu" class="filter-select">
            <option :value="null">Semua Business Unit</option>
            <option v-for="bu in buList" :key="bu.id" :value="bu.id">{{ bu.name }}</option>
          </select>
        </div>
        <button class="btn-primary" @click="openPlantForm()">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon-inline">
            <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          Tambah Plant
        </button>
      </div>

      <div class="card">
        <div class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>No</th>
                <th>Nama Plant</th>
                <th>Kode</th>
                <th>Business Unit</th>
                <th>Lokasi</th>
                <th>Status</th>
                <th>Dibuat</th>
                <th class="th-action">Aksi</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="plantLoading">
                <td colspan="8" class="td-empty td-loading">
                  <div class="spinner"></div>
                  <span>Memuat data…</span>
                </td>
              </tr>
              <tr v-else-if="!filteredPlants.length">
                <td colspan="8" class="td-empty">
                  {{ plantSearch ? 'Tidak ada hasil untuk "' + plantSearch + '"' : 'Belum ada data Plant' }}
                </td>
              </tr>
              <tr v-for="(item, idx) in pagedPlants" :key="item.id">
                <td class="td-num">{{ (plantPage - 1) * plantPer + idx + 1 }}</td>
                <td class="td-name">{{ item.name }}</td>
                <td><span class="code-badge">{{ item.code }}</span></td>
                <td>{{ buNameMap[item.businessUnitId] || '-' }}</td>
                <td class="td-desc">{{ item.location || '-' }}</td>
                <td>
                  <span :class="['status-pill', item.isActive ? 'pill-active' : 'pill-inactive']">
                    {{ item.isActive ? 'Aktif' : 'Nonaktif' }}
                  </span>
                </td>
                <td class="td-date">{{ formatDate(item.createdAt) }}</td>
                <td class="td-action">
                  <button class="btn-icon btn-edit" title="Ubah" @click="openPlantForm(item)">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                    </svg>
                  </button>
                  <button class="btn-icon btn-danger" title="Hapus" @click="confirmDeletePlant(item)">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                      <polyline points="3 6 5 6 21 6"/>
                      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                    </svg>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
          <PaginationBar :current-page="plantPage" :total-pages="plantPages" :total-items="plantTotal" :per-page="plantPer" @page="plantGo" @per-page="plantSetPer" />
        </div>
      </div>
    </div>

    <!-- ── Business Unit Modal ───────────────────────────────────── -->
    <div v-if="buModal.show" class="modal-overlay" @click.self="closeBuModal">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ buModal.editId ? 'Ubah Business Unit' : 'Tambah Business Unit' }}</h3>
          <button class="btn-close" @click="closeBuModal">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Nama <span class="req">*</span></label>
            <input v-model="buForm.name" type="text" placeholder="Nama business unit" class="form-input" />
          </div>
          <div class="form-group">
            <label>Kode <span class="req">*</span></label>
            <input v-model="buForm.code" type="text" placeholder="Kode unik (contoh: BU01)" class="form-input" maxlength="20" />
          </div>
          <div class="form-group">
            <label>Deskripsi</label>
            <textarea v-model="buForm.description" placeholder="Deskripsi (opsional)" class="form-input form-textarea" rows="3" />
          </div>
          <div class="form-group">
            <label>Status</label>
            <select v-model="buForm.isActive" class="form-input">
              <option :value="true">Aktif</option>
              <option :value="false">Nonaktif</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="closeBuModal" :disabled="buModal.saving">Batal</button>
          <button class="btn-primary" @click="saveBu" :disabled="buModal.saving">
            {{ buModal.saving ? 'Menyimpan…' : 'Simpan' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ── Plant Modal ───────────────────────────────────────────── -->
    <div v-if="plantModal.show" class="modal-overlay" @click.self="closePlantModal">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ plantModal.editId ? 'Ubah Plant' : 'Tambah Plant' }}</h3>
          <button class="btn-close" @click="closePlantModal">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Nama Plant <span class="req">*</span></label>
            <input v-model="plantForm.name" type="text" placeholder="Nama plant" class="form-input" />
          </div>
          <div class="form-group">
            <label>Kode <span class="req">*</span></label>
            <input v-model="plantForm.code" type="text" placeholder="Kode unik (contoh: PLT01)" class="form-input" maxlength="20" />
          </div>
          <div class="form-group">
            <label>Business Unit <span class="req">*</span></label>
            <select v-model="plantForm.businessUnitId" class="form-input">
              <option :value="null" disabled>Pilih Business Unit</option>
              <option v-for="bu in buList" :key="bu.id" :value="bu.id">{{ bu.name }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>Lokasi</label>
            <input v-model="plantForm.location" type="text" placeholder="Lokasi plant (opsional)" class="form-input" />
          </div>
          <div class="form-group">
            <label>Status</label>
            <select v-model="plantForm.isActive" class="form-input">
              <option :value="true">Aktif</option>
              <option :value="false">Nonaktif</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="closePlantModal" :disabled="plantModal.saving">Batal</button>
          <button class="btn-primary" @click="savePlant" :disabled="plantModal.saving">
            {{ plantModal.saving ? 'Menyimpan…' : 'Simpan' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ── User Tab ─────────────────────────────────────────────── -->
    <div v-if="activeTab === 'user'">
      <div class="section-bar">
        <div class="filter-group">
          <span class="total-badge">{{ filteredUsers.length }} data</span>
          <div class="search-box">
            <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <input v-model="userSearch" type="text" placeholder="Cari nama, email, username…" class="search-input" />
            <button v-if="userSearch" class="search-clear" @click="userSearch = ''">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
        </div>
        <button class="btn-primary" @click="openUserForm()">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon-inline">
            <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          Tambah Pengguna
        </button>
      </div>

      <div class="card">
        <div class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>No</th>
                <th>Nama Lengkap</th>
                <th>Username</th>
                <th>Email</th>
                <th>Peran</th>
                <th>Business Unit</th>
                <th>Plant</th>
                <th>Departemen</th>
                <th>Status</th>
                <th class="th-action">Aksi</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="userLoading">
                <td colspan="10" class="td-empty td-loading">
                  <div class="spinner"></div>
                  <span>Memuat data…</span>
                </td>
              </tr>
              <tr v-else-if="!filteredUsers.length">
                <td colspan="10" class="td-empty">
                  {{ userSearch ? 'Tidak ada hasil untuk "' + userSearch + '"' : 'Belum ada data Pengguna' }}
                </td>
              </tr>
              <tr v-for="(item, idx) in pagedUsers" :key="item.id">
                <td class="td-num">{{ (userPage - 1) * userPer + idx + 1 }}</td>
                <td class="td-name">{{ item.fullName || '-' }}</td>
                <td><span class="code-badge">{{ item.username || '-' }}</span></td>
                <td class="td-email">{{ item.email }}</td>
                <td>{{ roleNameMap[item.roleId] || '-' }}</td>
                <td>{{ buNameMap[item.businessUnitId] || '-' }}</td>
                <td>{{ plantNameMap[item.plantId] || '-' }}</td>
                <td>{{ deptNameMap[item.departmentId] || '-' }}</td>
                <td>
                  <span :class="['status-pill', item.isActive ? 'pill-active' : 'pill-inactive']">
                    {{ item.isActive ? 'Aktif' : 'Nonaktif' }}
                  </span>
                </td>
                <td class="td-action">
                  <button class="btn-icon btn-edit" title="Ubah" @click="openUserForm(item)">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                    </svg>
                  </button>
                  <button class="btn-icon btn-danger" title="Hapus" @click="confirmDeleteUser(item)">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                      <polyline points="3 6 5 6 21 6"/>
                      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                    </svg>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
          <PaginationBar :current-page="userPage" :total-pages="userPages" :total-items="userTotal" :per-page="userPer" @page="userGo" @per-page="userSetPer" />
        </div>
      </div>
    </div>

    <!-- ── Roles Tab ─────────────────────────────────────────────── -->
    <div v-if="activeTab === 'role'">
      <div class="section-bar">
        <div class="filter-group">
          <span class="total-badge">{{ filteredRoles.length }} data</span>
          <div class="search-box">
            <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <input v-model="roleSearch" type="text" placeholder="Cari nama peran…" class="search-input" />
            <button v-if="roleSearch" class="search-clear" @click="roleSearch = ''">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
        </div>
        <button v-if="roleLevel <= 2" class="btn-primary" @click="openRoleForm()">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon-inline">
            <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          Tambah Peran
        </button>
      </div>

      <div class="card">
        <div class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>No</th>
                <th>Nama Peran</th>
                <th>Level</th>
                <th>Deskripsi</th>
                <th v-if="roleLevel <= 2" class="th-action">Aksi</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="roleLoading">
                <td :colspan="roleLevel <= 2 ? 5 : 4" class="td-empty td-loading">
                  <div class="spinner"></div>
                  <span>Memuat data…</span>
                </td>
              </tr>
              <tr v-else-if="!filteredRoles.length">
                <td :colspan="roleLevel <= 2 ? 5 : 4" class="td-empty">
                  {{ roleSearch ? 'Tidak ada hasil untuk "' + roleSearch + '"' : 'Belum ada data Peran' }}
                </td>
              </tr>
              <tr v-for="(item, idx) in pagedRoles" :key="item.id">
                <td class="td-num">{{ (rolePage - 1) * rolePer + idx + 1 }}</td>
                <td class="td-name">{{ item.name }}</td>
                <td><span class="level-badge">Level {{ item.level }}</span></td>
                <td class="td-desc">{{ item.description || '-' }}</td>
                <td v-if="roleLevel <= 2" class="td-action">
                  <button class="btn-icon btn-edit" title="Ubah" @click="openRoleForm(item)">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                    </svg>
                  </button>
                  <button class="btn-icon btn-danger" title="Hapus" @click="confirmDeleteRole(item)">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                      <polyline points="3 6 5 6 21 6"/>
                      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                    </svg>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
          <PaginationBar :current-page="rolePage" :total-pages="rolePages" :total-items="roleTotal" :per-page="rolePer" @page="roleGo" @per-page="roleSetPer" />
        </div>
      </div>
    </div>

    <!-- ── Role Modal ───────────────────────────────────────────── -->
    <div v-if="roleModal.show" class="modal-overlay" @click.self="closeRoleModal">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h3>{{ roleModal.editId ? 'Ubah Peran' : 'Tambah Peran' }}</h3>
          <button class="btn-close" @click="closeRoleModal">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Nama Peran <span class="req">*</span></label>
            <input v-model="roleForm.name" type="text" placeholder="Contoh: Admin, Viewer" class="form-input" maxlength="50" />
          </div>
          <div class="form-group">
            <label>Level <span class="req">*</span>
              <span class="field-hint">— angka unik, makin kecil makin tinggi (0 = Admin/tertinggi)</span>
            </label>
            <input v-model.number="roleForm.level" type="number" min="0" placeholder="Contoh: 0, 1, 2, 3…" class="form-input" />
          </div>
          <div class="form-group">
            <label>Deskripsi</label>
            <textarea v-model="roleForm.description" placeholder="Deskripsi peran (opsional)" class="form-input form-textarea" rows="3" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="closeRoleModal" :disabled="roleModal.saving">Batal</button>
          <button class="btn-primary" @click="saveRole" :disabled="roleModal.saving">
            {{ roleModal.saving ? 'Menyimpan…' : 'Simpan' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ── User Modal ──────────────────────────────────────────── -->
    <div v-if="userModal.show" class="modal-overlay" @click.self="closeUserModal">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ userModal.editId ? 'Ubah Pengguna' : 'Tambah Pengguna' }}</h3>
          <button class="btn-close" @click="closeUserModal">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Nama Lengkap</label>
            <input v-model="userForm.fullName" type="text" placeholder="Nama lengkap" class="form-input" />
          </div>
          <div class="form-group">
            <label>Email <span class="req">*</span></label>
            <input v-model="userForm.email" type="email" placeholder="email@cp.co.id" class="form-input" />
          </div>
          <div class="form-group">
            <label>Username</label>
            <input v-model="userForm.username" type="text" placeholder="Username (opsional)" class="form-input" maxlength="50" />
          </div>
          <div class="form-group">
            <label>Password <span v-if="!userModal.editId" class="req">*</span></label>
            <input v-model="userForm.password" type="password"
              :placeholder="userModal.editId ? 'Kosongkan jika tidak ingin mengubah' : 'Password (min. 6 karakter)'"
              class="form-input" />
          </div>
          <div class="form-group">
            <label>Peran</label>
            <select v-model="userForm.roleId" class="form-input">
              <option :value="null">Tidak ada peran</option>
              <option v-for="r in roleList" :key="r.id" :value="r.id">{{ r.name }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>Business Unit</label>
            <select v-model="userForm.businessUnitId" class="form-input" @change="userForm.plantId = null">
              <option :value="null">Tidak ada</option>
              <option v-for="bu in buList" :key="bu.id" :value="bu.id">{{ bu.name }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>Plant</label>
            <select v-model="userForm.plantId" class="form-input">
              <option :value="null">Tidak ada</option>
              <option v-for="p in plantsForUserForm" :key="p.id" :value="p.id">{{ p.name }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>Departemen</label>
            <select v-model="userForm.departmentId" class="form-input">
              <option :value="null">Tidak ada</option>
              <option v-for="d in deptList" :key="d.id" :value="d.id">{{ d.name }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>Status</label>
            <select v-model="userForm.isActive" class="form-input">
              <option :value="true">Aktif</option>
              <option :value="false">Nonaktif</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="closeUserModal" :disabled="userModal.saving">Batal</button>
          <button class="btn-primary" @click="saveUser" :disabled="userModal.saving">
            {{ userModal.saving ? 'Menyimpan…' : 'Simpan' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ── Department Tab ──────────────────────────────────────── -->
    <div v-if="activeTab === 'dept'">
      <div class="section-bar">
        <div class="filter-group">
          <span class="total-badge">{{ filteredDepts.length }} data</span>
          <div class="search-box">
            <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <input v-model="deptSearch" type="text" placeholder="Cari nama atau kode…" class="search-input" />
            <button v-if="deptSearch" class="search-clear" @click="deptSearch = ''">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
        </div>
        <button class="btn-primary" @click="openDeptForm()">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon-inline">
            <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          Tambah Department
        </button>
      </div>

      <div class="card">
        <div class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>No</th>
                <th>Nama</th>
                <th>Kode</th>
                <th>Deskripsi</th>
                <th>Status</th>
                <th>Dibuat</th>
                <th class="th-action">Aksi</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="deptLoading">
                <td colspan="7" class="td-empty td-loading">
                  <div class="spinner"></div>
                  <span>Memuat data…</span>
                </td>
              </tr>
              <tr v-else-if="!filteredDepts.length">
                <td colspan="7" class="td-empty">
                  {{ deptSearch ? 'Tidak ada hasil untuk "' + deptSearch + '"' : 'Belum ada data Department' }}
                </td>
              </tr>
              <tr v-for="(item, idx) in pagedDepts" :key="item.id">
                <td class="td-num">{{ (deptPage - 1) * deptPer + idx + 1 }}</td>
                <td class="td-name">{{ item.name }}</td>
                <td><span class="code-badge">{{ item.code }}</span></td>
                <td class="td-desc">{{ item.description || '-' }}</td>
                <td>
                  <span :class="['status-pill', item.isActive ? 'pill-active' : 'pill-inactive']">
                    {{ item.isActive ? 'Aktif' : 'Nonaktif' }}
                  </span>
                </td>
                <td class="td-date">{{ formatDate(item.createdAt) }}</td>
                <td class="td-action">
                  <button class="btn-icon btn-edit" title="Ubah" @click="openDeptForm(item)">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                    </svg>
                  </button>
                  <button class="btn-icon btn-danger" title="Hapus" @click="confirmDeleteDept(item)">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                      <polyline points="3 6 5 6 21 6"/>
                      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                    </svg>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
          <PaginationBar :current-page="deptPage" :total-pages="deptPages" :total-items="deptTotal" :per-page="deptPer" @page="deptGo" @per-page="deptSetPer" />
        </div>
      </div>
    </div>

    <!-- ── Department Modal ─────────────────────────────────────── -->
    <div v-if="deptModal.show" class="modal-overlay" @click.self="closeDeptModal">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h3>{{ deptModal.editId ? 'Ubah Department' : 'Tambah Department' }}</h3>
          <button class="btn-close" @click="closeDeptModal">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Nama <span class="req">*</span></label>
            <input v-model="deptForm.name" type="text" placeholder="Nama department" class="form-input" />
          </div>
          <div class="form-group">
            <label>Kode <span class="req">*</span></label>
            <input v-model="deptForm.code" type="text" placeholder="Kode unik (contoh: DEPT01)" class="form-input" maxlength="20" />
          </div>
          <div class="form-group">
            <label>Deskripsi</label>
            <textarea v-model="deptForm.description" placeholder="Deskripsi (opsional)" class="form-input form-textarea" rows="3" />
          </div>
          <div class="form-group">
            <label>Status</label>
            <select v-model="deptForm.isActive" class="form-input">
              <option :value="true">Aktif</option>
              <option :value="false">Nonaktif</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="closeDeptModal" :disabled="deptModal.saving">Batal</button>
          <button class="btn-primary" @click="saveDept" :disabled="deptModal.saving">
            {{ deptModal.saving ? 'Menyimpan…' : 'Simpan' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ── Delete Confirm Modal ──────────────────────────────────── -->
    <div v-if="deleteModal.show" class="modal-overlay" @click.self="deleteModal.show = false">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h3>Konfirmasi Hapus</h3>
          <button class="btn-close" @click="deleteModal.show = false">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <p class="delete-msg">
            Hapus <strong>{{ deleteModal.name }}</strong>? Tindakan ini tidak dapat dibatalkan.
          </p>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="deleteModal.show = false" :disabled="deleteModal.loading">Batal</button>
          <button class="btn-danger" @click="executeDelete" :disabled="deleteModal.loading">
            {{ deleteModal.loading ? 'Menghapus…' : 'Hapus' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <transition name="toast-fade">
      <div v-if="toast.show" :class="['toast', `toast-${toast.type}`]">{{ toast.message }}</div>
    </transition>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue";
import { masterDataService } from "@/services/masterDataService";
import { usePagination } from "@/composables/usePagination.js";
import PaginationBar from "@/components/PaginationBar.vue";
import { authService } from "@/services/authService.js";

const roleLevel = authService.getRoleLevel();

// ── State ────────────────────────────────────────────────────────────────
const activeTab = ref("bu");

const buList = ref([]);
const buLoading = ref(false);
const buSearch = ref("");

const plantList = ref([]);
const plantLoading = ref(false);
const plantFilterBu = ref(null);
const plantSearch = ref("");

const roleList = ref([]);
const roleLoading = ref(false);
const roleSearch = ref("");

const userList = ref([]);
const userLoading = ref(false);
const userSearch = ref("");

const deptList = ref([]);
const deptLoading = ref(false);
const deptSearch = ref("");

// ── Computed ─────────────────────────────────────────────────────────────
const buNameMap = computed(() => {
  const map = {};
  buList.value.forEach((b) => (map[b.id] = b.name));
  return map;
});

const filteredBu = computed(() => {
  const q = buSearch.value.trim().toLowerCase();
  if (!q) return buList.value;
  return buList.value.filter(
    (b) =>
      b.name.toLowerCase().includes(q) ||
      b.code.toLowerCase().includes(q) ||
      (b.description || "").toLowerCase().includes(q),
  );
});

const filteredPlants = computed(() => {
  let list = plantList.value;
  if (plantFilterBu.value) list = list.filter((p) => p.businessUnitId === plantFilterBu.value);
  const q = plantSearch.value.trim().toLowerCase();
  if (!q) return list;
  return list.filter(
    (p) =>
      p.name.toLowerCase().includes(q) ||
      p.code.toLowerCase().includes(q) ||
      (p.location || "").toLowerCase().includes(q) ||
      (buNameMap.value[p.businessUnitId] || "").toLowerCase().includes(q),
  );
});

const roleNameMap = computed(() => {
  const map = {};
  roleList.value.forEach((r) => (map[r.id] = r.name));
  return map;
});

const filteredRoles = computed(() => {
  const q = roleSearch.value.trim().toLowerCase();
  if (!q) return [...roleList.value].sort((a, b) => a.level - b.level);
  return [...roleList.value]
    .filter((r) => r.name.toLowerCase().includes(q) || (r.description || "").toLowerCase().includes(q))
    .sort((a, b) => a.level - b.level);
});

const plantNameMap = computed(() => {
  const map = {};
  plantList.value.forEach((p) => (map[p.id] = p.name));
  return map;
});

const deptNameMap = computed(() => {
  const map = {};
  deptList.value.forEach((d) => (map[d.id] = d.name));
  return map;
});

const filteredDepts = computed(() => {
  const q = deptSearch.value.trim().toLowerCase();
  if (!q) return deptList.value;
  return deptList.value.filter(
    (d) =>
      d.name.toLowerCase().includes(q) ||
      d.code.toLowerCase().includes(q) ||
      (d.description || "").toLowerCase().includes(q),
  );
});

const filteredUsers = computed(() => {
  const q = userSearch.value.trim().toLowerCase();
  if (!q) return userList.value;
  return userList.value.filter(
    (u) =>
      (u.fullName || "").toLowerCase().includes(q) ||
      u.email.toLowerCase().includes(q) ||
      (u.username || "").toLowerCase().includes(q) ||
      (roleNameMap.value[u.roleId] || "").toLowerCase().includes(q) ||
      (buNameMap.value[u.businessUnitId] || "").toLowerCase().includes(q),
  );
});

// ── Pagination ───────────────────────────────────────────────────────────
const { currentPage: buPage, perPage: buPer, totalItems: buTotal, totalPages: buPages, paginatedItems: pagedBu, goToPage: buGo, setPerPage: buSetPer } = usePagination(filteredBu);
const { currentPage: plantPage, perPage: plantPer, totalItems: plantTotal, totalPages: plantPages, paginatedItems: pagedPlants, goToPage: plantGo, setPerPage: plantSetPer } = usePagination(filteredPlants);
const { currentPage: rolePage, perPage: rolePer, totalItems: roleTotal, totalPages: rolePages, paginatedItems: pagedRoles, goToPage: roleGo, setPerPage: roleSetPer } = usePagination(filteredRoles);
const { currentPage: userPage, perPage: userPer, totalItems: userTotal, totalPages: userPages, paginatedItems: pagedUsers, goToPage: userGo, setPerPage: userSetPer } = usePagination(filteredUsers);
const { currentPage: deptPage, perPage: deptPer, totalItems: deptTotal, totalPages: deptPages, paginatedItems: pagedDepts, goToPage: deptGo, setPerPage: deptSetPer } = usePagination(filteredDepts);

// ── Load data ────────────────────────────────────────────────────────────
async function loadBu() {
  buLoading.value = true;
  try {
    buList.value = await masterDataService.listBusinessUnits();
  } catch (e) {
    console.error("[MasterData] loadBu:", e);
  } finally {
    buLoading.value = false;
  }
}

async function loadPlants() {
  plantLoading.value = true;
  try {
    plantList.value = await masterDataService.listPlants();
  } catch (e) {
    console.error("[MasterData] loadPlants:", e);
  } finally {
    plantLoading.value = false;
  }
}

async function loadRoles() {
  roleLoading.value = true;
  try {
    roleList.value = await masterDataService.listRoles();
  } catch (e) {
    console.error("[MasterData] loadRoles:", e);
  } finally {
    roleLoading.value = false;
  }
}

async function loadUsers() {
  userLoading.value = true;
  try {
    userList.value = await masterDataService.listUsers();
  } catch (e) {
    console.error("[MasterData] loadUsers:", e);
  } finally {
    userLoading.value = false;
  }
}

async function loadDepts() {
  deptLoading.value = true;
  try {
    deptList.value = await masterDataService.listDepartments();
  } catch (e) {
    console.error("[MasterData] loadDepts:", e);
  } finally {
    deptLoading.value = false;
  }
}

onMounted(() => {
  loadBu();
  loadPlants();
  loadRoles();
  loadUsers();
  loadDepts();
});

// ── Business Unit form ───────────────────────────────────────────────────
const buModal = reactive({ show: false, editId: null, saving: false });
const buForm = reactive({ name: "", code: "", description: "", isActive: true });

function openBuForm(item = null) {
  buModal.editId = item?.id ?? null;
  buForm.name = item?.name ?? "";
  buForm.code = item?.code ?? "";
  buForm.description = item?.description ?? "";
  buForm.isActive = item?.isActive ?? true;
  buModal.show = true;
}

function closeBuModal() {
  buModal.show = false;
}

async function saveBu() {
  if (!buForm.name.trim()) return showToast("Nama wajib diisi", "error");
  if (!buForm.code.trim()) return showToast("Kode wajib diisi", "error");

  buModal.saving = true;
  try {
    const payload = {
      name: buForm.name.trim(),
      code: buForm.code.trim().toUpperCase(),
      description: buForm.description.trim() || null,
      isActive: buForm.isActive,
    };
    if (buModal.editId) {
      await masterDataService.updateBusinessUnit(buModal.editId, payload);
      showToast("Business unit berhasil diperbarui");
    } else {
      await masterDataService.createBusinessUnit(payload);
      showToast("Business unit berhasil ditambahkan");
    }
    closeBuModal();
    await loadBu();
  } catch (e) {
    console.error("[MasterData] saveBu:", e);
  } finally {
    buModal.saving = false;
  }
}

// ── Plant form ───────────────────────────────────────────────────────────
const plantModal = reactive({ show: false, editId: null, saving: false });
const plantForm = reactive({ name: "", code: "", businessUnitId: null, location: "", isActive: true });

function openPlantForm(item = null) {
  plantModal.editId = item?.id ?? null;
  plantForm.name = item?.name ?? "";
  plantForm.code = item?.code ?? "";
  plantForm.businessUnitId = item?.businessUnitId ?? null;
  plantForm.location = item?.location ?? "";
  plantForm.isActive = item?.isActive ?? true;
  plantModal.show = true;
}

function closePlantModal() {
  plantModal.show = false;
}

async function savePlant() {
  if (!plantForm.name.trim()) return showToast("Nama wajib diisi", "error");
  if (!plantForm.code.trim()) return showToast("Kode wajib diisi", "error");
  if (!plantForm.businessUnitId) return showToast("Business Unit wajib dipilih", "error");

  plantModal.saving = true;
  try {
    const payload = {
      name: plantForm.name.trim(),
      code: plantForm.code.trim().toUpperCase(),
      businessUnitId: plantForm.businessUnitId,
      location: plantForm.location.trim() || null,
      isActive: plantForm.isActive,
    };
    if (plantModal.editId) {
      await masterDataService.updatePlant(plantModal.editId, payload);
      showToast("Plant berhasil diperbarui");
    } else {
      await masterDataService.createPlant(payload);
      showToast("Plant berhasil ditambahkan");
    }
    closePlantModal();
    await loadPlants();
  } catch (e) {
    console.error("[MasterData] savePlant:", e);
  } finally {
    plantModal.saving = false;
  }
}

// ── Role form ────────────────────────────────────────────────────────────
const roleModal = reactive({ show: false, editId: null, saving: false });
const roleForm = reactive({ name: "", level: null, description: "" });

function openRoleForm(item = null) {
  roleModal.editId = item?.id ?? null;
  roleForm.name = item?.name ?? "";
  roleForm.level = item?.level ?? null;
  roleForm.description = item?.description ?? "";
  roleModal.show = true;
}

function closeRoleModal() {
  roleModal.show = false;
}

async function saveRole() {
  if (!roleForm.name.trim()) return showToast("Nama peran wajib diisi", "error");
  if (roleForm.level === null || roleForm.level === "" || roleForm.level < 0) return showToast("Level wajib diisi (angka ≥ 0)", "error");

  roleModal.saving = true;
  try {
    const payload = {
      name: roleForm.name.trim(),
      level: roleForm.level,
      description: roleForm.description.trim() || null,
    };
    if (roleModal.editId) {
      await masterDataService.updateRole(roleModal.editId, payload);
      showToast("Peran berhasil diperbarui");
    } else {
      await masterDataService.createRole(payload);
      showToast("Peran berhasil ditambahkan");
    }
    closeRoleModal();
    await loadRoles();
  } catch (e) {
    showToast(e.message, "error");
  } finally {
    roleModal.saving = false;
  }
}

// ── User form ────────────────────────────────────────────────────────────
const userModal = reactive({ show: false, editId: null, saving: false });
const userForm = reactive({
  email: "", password: "", username: "", fullName: "",
  roleId: null, businessUnitId: null, plantId: null, departmentId: null, isActive: true,
});

const plantsForUserForm = computed(() =>
  userForm.businessUnitId
    ? plantList.value.filter((p) => p.businessUnitId === userForm.businessUnitId)
    : plantList.value,
);

function openUserForm(item = null) {
  userModal.editId = item?.id ?? null;
  userForm.email = item?.email ?? "";
  userForm.password = "";
  userForm.username = item?.username ?? "";
  userForm.fullName = item?.fullName ?? "";
  userForm.roleId = item?.roleId ?? null;
  userForm.businessUnitId = item?.businessUnitId ?? null;
  userForm.plantId = item?.plantId ?? null;
  userForm.departmentId = item?.departmentId ?? null;
  userForm.isActive = item?.isActive ?? true;
  userModal.show = true;
}

function closeUserModal() {
  userModal.show = false;
}

async function saveUser() {
  if (!userForm.email.trim()) return showToast("Email wajib diisi", "error");
  if (!userModal.editId && !userForm.password.trim()) return showToast("Password wajib diisi", "error");

  userModal.saving = true;
  try {
    const payload = {
      email: userForm.email.trim(),
      username: userForm.username.trim() || null,
      fullName: userForm.fullName.trim() || null,
      roleId: userForm.roleId,
      businessUnitId: userForm.businessUnitId,
      plantId: userForm.plantId,
      departmentId: userForm.departmentId,
      isActive: userForm.isActive,
    };
    if (userModal.editId) {
      if (userForm.password.trim()) payload.password = userForm.password.trim();
      await masterDataService.updateUser(userModal.editId, payload);
      showToast("Pengguna berhasil diperbarui");
    } else {
      payload.password = userForm.password.trim();
      await masterDataService.createUser(payload);
      showToast("Pengguna berhasil ditambahkan");
    }
    closeUserModal();
    await loadUsers();
  } catch (e) {
    showToast(e.message, "error");
  } finally {
    userModal.saving = false;
  }
}

// ── Department form ──────────────────────────────────────────────────────
const deptModal = reactive({ show: false, editId: null, saving: false });
const deptForm = reactive({ name: "", code: "", description: "", isActive: true });

function openDeptForm(item = null) {
  deptModal.editId = item?.id ?? null;
  deptForm.name = item?.name ?? "";
  deptForm.code = item?.code ?? "";
  deptForm.description = item?.description ?? "";
  deptForm.isActive = item?.isActive ?? true;
  deptModal.show = true;
}

function closeDeptModal() {
  deptModal.show = false;
}

async function saveDept() {
  if (!deptForm.name.trim()) return showToast("Nama wajib diisi", "error");
  if (!deptForm.code.trim()) return showToast("Kode wajib diisi", "error");

  deptModal.saving = true;
  try {
    const payload = {
      name: deptForm.name.trim(),
      code: deptForm.code.trim().toUpperCase(),
      description: deptForm.description.trim() || null,
      isActive: deptForm.isActive,
    };
    if (deptModal.editId) {
      await masterDataService.updateDepartment(deptModal.editId, payload);
      showToast("Department berhasil diperbarui");
    } else {
      await masterDataService.createDepartment(payload);
      showToast("Department berhasil ditambahkan");
    }
    closeDeptModal();
    await loadDepts();
  } catch (e) {
    showToast(e.message, "error");
  } finally {
    deptModal.saving = false;
  }
}

// ── Delete ───────────────────────────────────────────────────────────────
const deleteModal = reactive({ show: false, name: "", type: "", id: null, loading: false });

function confirmDeleteBu(item) {
  deleteModal.type = "bu";
  deleteModal.id = item.id;
  deleteModal.name = item.name;
  deleteModal.show = true;
}

function confirmDeletePlant(item) {
  deleteModal.type = "plant";
  deleteModal.id = item.id;
  deleteModal.name = item.name;
  deleteModal.show = true;
}

function confirmDeleteRole(item) {
  deleteModal.type = "role";
  deleteModal.id = item.id;
  deleteModal.name = item.name;
  deleteModal.show = true;
}

function confirmDeleteUser(item) {
  deleteModal.type = "user";
  deleteModal.id = item.id;
  deleteModal.name = item.fullName || item.email;
  deleteModal.show = true;
}

function confirmDeleteDept(item) {
  deleteModal.type = "dept";
  deleteModal.id = item.id;
  deleteModal.name = item.name;
  deleteModal.show = true;
}

async function executeDelete() {
  deleteModal.loading = true;
  try {
    if (deleteModal.type === "bu") {
      await masterDataService.deleteBusinessUnit(deleteModal.id);
      showToast("Business unit berhasil dihapus");
      await loadBu();
      await loadPlants();
    } else if (deleteModal.type === "plant") {
      await masterDataService.deletePlant(deleteModal.id);
      showToast("Plant berhasil dihapus");
      await loadPlants();
    } else if (deleteModal.type === "role") {
      await masterDataService.deleteRole(deleteModal.id);
      showToast("Peran berhasil dihapus");
      await loadRoles();
    } else if (deleteModal.type === "dept") {
      await masterDataService.deleteDepartment(deleteModal.id);
      showToast("Department berhasil dihapus");
      await loadDepts();
    } else {
      await masterDataService.deleteUser(deleteModal.id);
      showToast("Pengguna berhasil dihapus");
      await loadUsers();
    }
    deleteModal.show = false;
  } catch (e) {
    showToast(e.message, "error");
  } finally {
    deleteModal.loading = false;
  }
}

// ── Toast ────────────────────────────────────────────────────────────────
const toast = reactive({ show: false, message: "", type: "success" });
let toastTimer = null;

function showToast(msg, type = "success") {
  if (toastTimer) clearTimeout(toastTimer);
  toast.show = true;
  toast.message = msg;
  toast.type = type;
  toastTimer = setTimeout(() => (toast.show = false), 4000);
}

// ── Helpers ──────────────────────────────────────────────────────────────
function formatDate(val) {
  if (!val) return "-";
  const d = new Date(val);
  if (isNaN(d)) return val;
  return d.toLocaleDateString("id-ID", { day: "2-digit", month: "short", year: "numeric" });
}
</script>

<style scoped>
.master-data {
  padding: 28px 32px;
}
@media (max-width: 1024px) { .master-data { padding: 20px 20px; } }
@media (max-width: 640px)  { .master-data { padding: 16px 14px; } }

/* Header */
.page-header {
  margin-bottom: 20px;
}
.page-title {
  font-size: 22px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 4px;
}
.page-sub {
  font-size: 13px;
  color: #64748b;
  margin: 0;
}

/* Tabs */
.tabs {
  display: flex;
  gap: 4px;
  background: #f1f5f9;
  border-radius: 10px;
  padding: 4px;
  margin-bottom: 20px;
  flex-wrap: nowrap;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}
.tabs::-webkit-scrollbar { display: none; }
.tab-btn {
  padding: 8px 20px;
  border-radius: 7px;
  border: none;
  background: transparent;
  font-size: 14px;
  font-weight: 500;
  color: #64748b;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
  flex-shrink: 0;
}
.tab-btn.active {
  background: #fff;
  color: #1e293b;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

/* Section bar */
.section-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  gap: 12px;
  flex-wrap: nowrap;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}
.section-bar::-webkit-scrollbar { display: none; }
.filter-group {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: nowrap;
  flex-shrink: 0;
}
.total-badge {
  font-size: 13px;
  color: #64748b;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  padding: 3px 10px;
}
.filter-select {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 7px 10px;
  font-size: 13px;
  color: #1e293b;
  background: #fff;
  outline: none;
  flex-shrink: 0;
  white-space: nowrap;
}
.filter-select:focus { border-color: #3b82f6; }

.search-box {
  position: relative;
  display: flex;
  align-items: center;
}
.search-icon {
  position: absolute;
  left: 10px;
  width: 15px;
  height: 15px;
  color: #94a3b8;
  pointer-events: none;
}
.search-input {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 7px 32px 7px 32px;
  font-size: 13px;
  color: #1e293b;
  background: #fff;
  outline: none;
  width: 200px;
  transition: border-color 0.15s, width 0.2s;
}
.search-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59,130,246,0.1);
  width: 240px;
}
.search-clear {
  position: absolute;
  right: 8px;
  width: 18px;
  height: 18px;
  border: none;
  background: transparent;
  color: #94a3b8;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}
.search-clear:hover { color: #374151; }
.search-clear svg { width: 13px; height: 13px; }

/* Card + table */
.card {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  overflow: hidden;
}
.table-wrap {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  min-width: 600px;
}
.data-table th {
  background: #f8fafc;
  padding: 11px 14px;
  text-align: center;
  font-weight: 600;
  color: #475569;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  border-bottom: 1px solid #e2e8f0;
  white-space: nowrap;
}
.data-table td {
  padding: 12px 14px;
  text-align: left;
  border-bottom: 1px solid #f1f5f9;
  color: #374151;
  vertical-align: middle;
}
/* Status column centered (matches action column) */
.data-table td:has(.status-pill) {
  text-align: center;
}
/* Vertical dividers between columns */
.data-table th:not(:first-child),
.data-table td:not(:first-child) {
  border-left: 1px solid #e2e8f0;
}
.data-table tbody tr:last-child td { border-bottom: none; }
.data-table tbody tr:hover td { background: #f8fafc; }

.data-table td.td-num { color: #94a3b8; font-size: 12px; width: 40px; text-align: center; }
.td-name { font-weight: 600; color: #1e293b; }
.td-desc { color: #64748b; max-width: 220px; }
.td-date { color: #64748b; white-space: nowrap; }
.td-email { color: #64748b; font-size: 12px; }
.td-empty { text-align: center; color: #94a3b8; padding: 40px 0; font-size: 13px; }
.td-loading { display: flex; align-items: center; justify-content: center; gap: 10px; }
.td-loading .spinner, .td-empty .spinner {
  width: 18px; height: 18px;
  border: 2px solid #e2e8f0; border-top-color: #3b82f6;
  border-radius: 50%; animation: spin 0.7s linear infinite; flex-shrink: 0;
}
@keyframes spin { to { transform: rotate(360deg); } }
.th-action { text-align: center; width: 90px; }
.td-action { text-align: center; white-space: nowrap; display: flex; align-items: center; justify-content: center; gap: 6px; }

.code-badge {
  display: inline-block;
  background: #eff6ff;
  color: #2563eb;
  border-radius: 5px;
  padding: 2px 8px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.3px;
}
.level-badge {
  display: inline-block;
  background: #f0fdf4;
  color: #16a34a;
  border-radius: 5px;
  padding: 2px 8px;
  font-size: 12px;
  font-weight: 600;
}
.field-hint {
  font-size: 11px;
  font-weight: 400;
  color: #94a3b8;
}
.status-pill {
  display: inline-block;
  border-radius: 20px;
  padding: 3px 10px;
  font-size: 12px;
  font-weight: 600;
}
.pill-active { background: #dcfce7; color: #16a34a; }
.pill-inactive { background: #f1f5f9; color: #94a3b8; }

/* Inline SVG icon inside text buttons */
.btn-icon-inline { width: 16px; height: 16px; flex-shrink: 0; }

/* Action buttons */
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
  transition: background 0.15s, color 0.15s;
  position: relative;
}
.btn-icon:hover { background: #e2e8f0; color: #3b82f6; }
.btn-edit { color: #2563eb; }
.btn-edit:hover { background: #eff6ff; }
.btn-danger { background: #fef2f2; color: #ef4444; }
.btn-danger:hover { background: #fee2e2; color: #dc2626; }

/* Modal max-width override for this page */
.modal { max-width: 460px; }
.modal-sm { max-width: 360px; }

/* Form inside modal */
.form-group { display: flex; flex-direction: column; gap: 5px; }
.form-group label { font-size: 13px; font-weight: 600; color: #374151; }
.req { color: #ef4444; }
.form-textarea { resize: vertical; min-height: 80px; }

.delete-msg { font-size: 14px; color: #374151; line-height: 1.5; margin: 0; }

/* Toast */
.toast {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  z-index: 500;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  white-space: nowrap;
}
.toast-success { background: #f0fdf4; color: #166534; border: 1px solid #bbf7d0; }
.toast-error { background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }
.toast-warning { background: #fffbeb; color: #92400e; border: 1px solid #fde68a; }
.toast-fade-enter-active, .toast-fade-leave-active { transition: opacity 0.3s, transform 0.3s; }
.toast-fade-enter-from, .toast-fade-leave-to { opacity: 0; transform: translateX(-50%) translateY(8px); }

/* Mobile */
@media (max-width: 767px) {
  .master-data { padding: 16px; }
  .section-bar { flex-direction: column; align-items: flex-start; }
  .btn-primary { width: 100%; justify-content: center; }
  .tabs { width: 100%; }
  .tab-btn { flex: 1; text-align: center; }
}
</style>
