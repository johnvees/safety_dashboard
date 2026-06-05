import { makeCache } from '@/utils/apiCache.js';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
const GRAPHQL_URL = `${API_BASE}/graphql`;

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

export const caseIncidentService = {
  async list() {
    const hit = _cache.get('ci_list');
    if (hit) return hit;
    const data = await gql(`
      query {
        caseIncidentList {
          id namaPelapor pelaporDeptId
          namaSaksi saksiDeptId
          tanggalKejadian tanggalPelaporan
          namaKorban korbanDeptId statusKaryawan
          jenisKecelakaan lokasiKecelakaan
          deskripsiKecelakaan penyebabKecelakaan perbaikanDilakukan
          saksiList fotoKejadian targetPenyelesaian status
          createdBy createdAt updatedAt
        }
      }
    `);
    _cache.set('ci_list', data.caseIncidentList);
    return data.caseIncidentList;
  },

  async create(input) {
    const data = await gql(
      `mutation CreateCaseIncident(
        $namaPelapor: String!,
        $tanggalKejadian: String!,
        $tanggalPelaporan: String!,
        $namaKorban: String!,
        $pelaporDeptId: Int,
        $namaSaksi: String,
        $saksiDeptId: Int,
        $korbanDeptId: Int,
        $statusKaryawan: String,
        $jenisKecelakaan: String,
        $lokasiKecelakaan: String,
        $deskripsiKecelakaan: String,
        $penyebabKecelakaan: String,
        $perbaikanDilakukan: String,
        $saksiList: String,
        $fotoKejadian: String,
        $targetPenyelesaian: String,
        $status: String
      ) {
        createCaseIncident(
          namaPelapor: $namaPelapor,
          tanggalKejadian: $tanggalKejadian,
          tanggalPelaporan: $tanggalPelaporan,
          namaKorban: $namaKorban,
          pelaporDeptId: $pelaporDeptId,
          namaSaksi: $namaSaksi,
          saksiDeptId: $saksiDeptId,
          korbanDeptId: $korbanDeptId,
          statusKaryawan: $statusKaryawan,
          jenisKecelakaan: $jenisKecelakaan,
          lokasiKecelakaan: $lokasiKecelakaan,
          deskripsiKecelakaan: $deskripsiKecelakaan,
          penyebabKecelakaan: $penyebabKecelakaan,
          perbaikanDilakukan: $perbaikanDilakukan,
          saksiList: $saksiList,
          fotoKejadian: $fotoKejadian,
          targetPenyelesaian: $targetPenyelesaian,
          status: $status
        ) {
          success message
          incident { id namaKorban status createdAt }
        }
      }`,
      input,
    );
    const result = data.createCaseIncident;
    if (!result.success) throw new Error(result.message);
    _cache.del('ci_list');
    return result;
  },

  async update(id, input) {
    const data = await gql(
      `mutation UpdateCaseIncident(
        $id: Int!,
        $namaPelapor: String,
        $tanggalKejadian: String,
        $tanggalPelaporan: String,
        $namaKorban: String,
        $pelaporDeptId: Int,
        $namaSaksi: String,
        $saksiDeptId: Int,
        $korbanDeptId: Int,
        $statusKaryawan: String,
        $jenisKecelakaan: String,
        $lokasiKecelakaan: String,
        $deskripsiKecelakaan: String,
        $penyebabKecelakaan: String,
        $perbaikanDilakukan: String,
        $saksiList: String,
        $fotoKejadian: String,
        $targetPenyelesaian: String,
        $status: String
      ) {
        updateCaseIncident(
          id: $id,
          namaPelapor: $namaPelapor,
          tanggalKejadian: $tanggalKejadian,
          tanggalPelaporan: $tanggalPelaporan,
          namaKorban: $namaKorban,
          pelaporDeptId: $pelaporDeptId,
          namaSaksi: $namaSaksi,
          saksiDeptId: $saksiDeptId,
          korbanDeptId: $korbanDeptId,
          statusKaryawan: $statusKaryawan,
          jenisKecelakaan: $jenisKecelakaan,
          lokasiKecelakaan: $lokasiKecelakaan,
          deskripsiKecelakaan: $deskripsiKecelakaan,
          penyebabKecelakaan: $penyebabKecelakaan,
          perbaikanDilakukan: $perbaikanDilakukan,
          saksiList: $saksiList,
          fotoKejadian: $fotoKejadian,
          targetPenyelesaian: $targetPenyelesaian,
          status: $status
        ) {
          success message
          incident { id namaKorban status updatedAt }
        }
      }`,
      { id, ...input },
    );
    const result = data.updateCaseIncident;
    if (!result.success) throw new Error(result.message);
    _cache.del('ci_list');
    return result;
  },

  async delete(id) {
    const data = await gql(
      `mutation DeleteCaseIncident($id: Int!) {
        deleteCaseIncident(id: $id) { success message }
      }`,
      { id },
    );
    const result = data.deleteCaseIncident;
    if (!result.success) throw new Error(result.message);
    _cache.del('ci_list');
    return result;
  },
};
