const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
const GRAPHQL_URL = `${API_BASE}/graphql`;
const UPLOAD_URL = `${API_BASE}/upload`;

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

const REPORT_FIELDS = `
  id tanggal pekerjaan pekerja lokasiPekerjaan
  statusPermit noPermit jenisPekerjaan jenisPekerjaanLainnya
  potensiBahaya levelRisiko pengendalianBahaya
  pengawasHse saranMasukan foto
  departmentId departmentName businessUnitId businessUnitName plantId plantName createdBy
  createdAt updatedAt
`;

export const hseDailyService = {
  async listDepartments() {
    const data = await gql(`query { departments { id name } }`);
    return data.departments;
  },

  async list() {
    const data = await gql(`query { hseDailyList { ${REPORT_FIELDS} } }`);
    return data.hseDailyList;
  },

  async getById(id) {
    const data = await gql(
      `query GetHseDaily($id: Int!) { hseDailyById(id: $id) { ${REPORT_FIELDS} } }`,
      { id },
    );
    return data.hseDailyById;
  },

  async create(input) {
    const data = await gql(
      `mutation CreateHseDaily(
        $tanggal: String!, $pekerjaan: String!, $pekerja: String!,
        $lokasiPekerjaan: String, $statusPermit: Boolean, $noPermit: String,
        $jenisPekerjaan: String, $jenisPekerjaanLainnya: String,
        $potensiBahaya: String, $levelRisiko: String, $pengendalianBahaya: String,
        $pengawasHse: String, $saranMasukan: String, $foto: String,
        $departmentId: Int, $businessUnitId: Int, $plantId: Int
      ) {
        createHseDaily(
          tanggal: $tanggal, pekerjaan: $pekerjaan, pekerja: $pekerja,
          lokasiPekerjaan: $lokasiPekerjaan, statusPermit: $statusPermit, noPermit: $noPermit,
          jenisPekerjaan: $jenisPekerjaan, jenisPekerjaanLainnya: $jenisPekerjaanLainnya,
          potensiBahaya: $potensiBahaya, levelRisiko: $levelRisiko, pengendalianBahaya: $pengendalianBahaya,
          pengawasHse: $pengawasHse, saranMasukan: $saranMasukan, foto: $foto,
          departmentId: $departmentId, businessUnitId: $businessUnitId, plantId: $plantId
        ) { success message report { id tanggal createdAt } }
      }`,
      input,
    );
    const result = data.createHseDaily;
    if (!result.success) throw new Error(result.message);
    return result;
  },

  async update(id, input) {
    const data = await gql(
      `mutation UpdateHseDaily(
        $id: Int!, $tanggal: String, $pekerjaan: String, $pekerja: String,
        $lokasiPekerjaan: String, $statusPermit: Boolean, $noPermit: String,
        $jenisPekerjaan: String, $jenisPekerjaanLainnya: String,
        $potensiBahaya: String, $levelRisiko: String, $pengendalianBahaya: String,
        $pengawasHse: String, $saranMasukan: String, $foto: String,
        $departmentId: Int, $businessUnitId: Int, $plantId: Int
      ) {
        updateHseDaily(
          id: $id, tanggal: $tanggal, pekerjaan: $pekerjaan, pekerja: $pekerja,
          lokasiPekerjaan: $lokasiPekerjaan, statusPermit: $statusPermit, noPermit: $noPermit,
          jenisPekerjaan: $jenisPekerjaan, jenisPekerjaanLainnya: $jenisPekerjaanLainnya,
          potensiBahaya: $potensiBahaya, levelRisiko: $levelRisiko, pengendalianBahaya: $pengendalianBahaya,
          pengawasHse: $pengawasHse, saranMasukan: $saranMasukan, foto: $foto,
          departmentId: $departmentId, businessUnitId: $businessUnitId, plantId: $plantId
        ) { success message report { id tanggal updatedAt } }
      }`,
      { id, ...input },
    );
    const result = data.updateHseDaily;
    if (!result.success) throw new Error(result.message);
    return result;
  },

  async delete(id) {
    const data = await gql(
      `mutation DeleteHseDaily($id: Int!) {
        deleteHseDaily(id: $id) { success message }
      }`,
      { id },
    );
    const result = data.deleteHseDaily;
    if (!result.success) throw new Error(result.message);
    return result;
  },
};
