import { makeCache } from '@/utils/apiCache.js';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
const GRAPHQL_URL = `${API_BASE}/graphql`;
const UPLOAD_URL = `${API_BASE}/upload`;

const _cache = makeCache();

async function gql(query, variables = {}) {
  const token = localStorage.getItem("token");
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(GRAPHQL_URL, {
    method: "POST",
    headers,
    body: JSON.stringify({ query, variables }),
  });

  if (!res.ok) throw new Error(`Server error: ${res.status}`);
  const { data, errors } = await res.json();
  if (errors?.length) throw new Error(errors[0].message);
  return data;
}

export async function uploadImage(file) {
  const token = localStorage.getItem("token");
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(UPLOAD_URL, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Upload failed: ${res.status}`);
  }

  const { url } = await res.json();
  return url;
}

export const inspectionK3LService = {
  async listBusinessUnits() {
    const hit = _cache.get('bu');
    if (hit) return hit;
    const data = await gql(`
      query {
        businessUnits {
          id name
        }
      }
    `);
    _cache.set('bu', data.businessUnits);
    return data.businessUnits;
  },

  async listDepartments() {
    const hit = _cache.get('dept');
    if (hit) return hit;
    const data = await gql(`
      query {
        departments {
          id name
        }
      }
    `);
    _cache.set('dept', data.departments);
    return data.departments;
  },

  async listPlants(businessUnitId = null) {
    const key = 'plants:' + businessUnitId;
    const hit = _cache.get(key);
    if (hit) return hit;
    const data = await gql(
      `query Plants($businessUnitId: Int) {
        plants(businessUnitId: $businessUnitId) {
          id name businessUnitId
        }
      }`,
      { businessUnitId },
    );
    _cache.set(key, data.plants);
    return data.plants;
  },

  async list() {
    const hit = _cache.get('list');
    if (hit) return hit;
    const data = await gql(`
      query {
        inspectionK3lList {
          id tanggal kategoriTemuan deskripsiTemuan
          fotoSebelum fotoSesudah lokasi
          tindakanPerbaikan targetSelesai
          status aktualClose
          businessUnitId plantId departmentId
          saranPerbaikan tindakanPerbaikan
          ditindaklanjutiOleh ditindaklanjutiDepartmentId tanggalTindaklanjuti
          jenisInspeksi pelaporUsername pelaporDepartmentId tanggalPelaporan
          divalidasiOleh divalidasiDepartmentId tanggalValidasi alasanValidasi statusValidasi
          tindakLanjutCount
          tindakLanjutList {
            id roundNumber tindakanPerbaikan fotoSesudah
            ditindaklanjutiOleh ditindaklanjutiDepartmentId tanggalTindaklanjuti
          }
          validasiCount
          validasiList {
            id roundNumber divalidasiOleh divalidasiDepartmentId
            tanggalValidasi alasanValidasi statusValidasi
          }
          createdAt updatedAt commentCount
        }
      }
    `);
    _cache.set('list', data.inspectionK3lList);
    return data.inspectionK3lList;
  },

  async getById(id) {
    const data = await gql(
      `query GetInspection($id: Int!) {
        inspectionK3lById(id: $id) {
          id tanggal kategoriTemuan deskripsiTemuan
          fotoSebelum fotoSesudah lokasi
          tindakanPerbaikan targetSelesai
          status aktualClose
          businessUnitId plantId departmentId
          jenisInspeksi createdAt updatedAt commentCount
        }
      }`,
      { id },
    );
    return data.inspectionK3lById;
  },

  async create(input) {
    const data = await gql(
      `mutation CreateInspectionK3L(
        $tanggal: String!,
        $kategoriTemuan: String!,
        $deskripsiTemuan: String,
        $fotoSebelum: String,
        $fotoSesudah: String,
        $lokasi: String,
        $tindakanPerbaikan: String,
        $targetSelesai: String,
        $status: String,
        $aktualClose: String,
        $businessUnitId: Int,
        $plantId: Int,
        $departmentId: Int,
        $jenisInspeksi: String
      ) {
        createInspectionK3l(
          tanggal: $tanggal,
          kategoriTemuan: $kategoriTemuan,
          deskripsiTemuan: $deskripsiTemuan,
          fotoSebelum: $fotoSebelum,
          fotoSesudah: $fotoSesudah,
          lokasi: $lokasi,
          tindakanPerbaikan: $tindakanPerbaikan,
          targetSelesai: $targetSelesai,
          status: $status,
          aktualClose: $aktualClose,
          businessUnitId: $businessUnitId,
          plantId: $plantId,
          departmentId: $departmentId,
          jenisInspeksi: $jenisInspeksi
        ) {
          success message
          inspection {
            id tanggal kategoriTemuan deskripsiTemuan
            lokasi status createdAt
          }
        }
      }`,
      input,
    );
    const result = data.createInspectionK3l;
    if (!result.success) throw new Error(result.message);
    _cache.del('list');
    return result;
  },

  async update(id, input) {
    const data = await gql(
      `mutation UpdateInspectionK3L(
        $id: Int!,
        $tanggal: String,
        $kategoriTemuan: String,
        $deskripsiTemuan: String,
        $fotoSebelum: String,
        $fotoSesudah: String,
        $lokasi: String,
        $tindakanPerbaikan: String,
        $targetSelesai: String,
        $status: String,
        $aktualClose: String,
        $businessUnitId: Int,
        $plantId: Int,
        $departmentId: Int,
        $jenisInspeksi: String
      ) {
        updateInspectionK3l(
          id: $id,
          tanggal: $tanggal,
          kategoriTemuan: $kategoriTemuan,
          deskripsiTemuan: $deskripsiTemuan,
          fotoSebelum: $fotoSebelum,
          fotoSesudah: $fotoSesudah,
          lokasi: $lokasi,
          tindakanPerbaikan: $tindakanPerbaikan,
          targetSelesai: $targetSelesai,
          status: $status,
          aktualClose: $aktualClose,
          businessUnitId: $businessUnitId,
          plantId: $plantId,
          departmentId: $departmentId,
          jenisInspeksi: $jenisInspeksi
        ) {
          success message
          inspection {
            id tanggal kategoriTemuan deskripsiTemuan
            lokasi status updatedAt
          }
        }
      }`,
      { id, ...input },
    );
    const result = data.updateInspectionK3l;
    if (!result.success) throw new Error(result.message);
    _cache.del('list');
    return result;
  },

  async tindakLanjut(id, input) {
    const data = await gql(
      `mutation TindakLanjut(
        $id: Int!, $tindakanPerbaikan: String, $fotoSesudah: String, $ditindaklanjutiDepartmentId: Int
      ) {
        tindakLanjutInspectionK3l(
          id: $id, tindakanPerbaikan: $tindakanPerbaikan,
          fotoSesudah: $fotoSesudah, ditindaklanjutiDepartmentId: $ditindaklanjutiDepartmentId
        ) {
          success message
          inspection { id status tindakanPerbaikan ditindaklanjutiOleh tanggalTindaklanjuti }
        }
      }`,
      { id, ...input },
    );
    const result = data.tindakLanjutInspectionK3l;
    if (!result.success) throw new Error(result.message);
    _cache.del('list');
    return result;
  },

  async validasi(id, input) {
    const data = await gql(
      `mutation Validasi(
        $id: Int!, $alasanValidasi: String, $statusValidasi: String, $divalidasiDepartmentId: Int, $aktualClose: String
      ) {
        validasiInspectionK3l(
          id: $id, alasanValidasi: $alasanValidasi,
          statusValidasi: $statusValidasi, divalidasiDepartmentId: $divalidasiDepartmentId, aktualClose: $aktualClose
        ) {
          success message
          inspection { id status statusValidasi divalidasiOleh tanggalValidasi aktualClose }
        }
      }`,
      { id, ...input },
    );
    const result = data.validasiInspectionK3l;
    if (!result.success) throw new Error(result.message);
    _cache.del('list');
    return result;
  },

  async delete(id) {
    const data = await gql(
      `mutation DeleteInspectionK3L($id: Int!) {
        deleteInspectionK3l(id: $id) {
          success message
        }
      }`,
      { id },
    );
    const result = data.deleteInspectionK3l;
    if (!result.success) throw new Error(result.message);
    _cache.del('list');
    return result;
  },
};
