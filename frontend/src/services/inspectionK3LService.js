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

export const inspectionK3LService = {
  async listBusinessUnits() {
    const data = await gql(`
      query {
        businessUnits {
          id name
        }
      }
    `);
    return data.businessUnits;
  },

  async listDepartments() {
    const data = await gql(`
      query {
        departments {
          id name
        }
      }
    `);
    return data.departments;
  },

  async listPlants(businessUnitId = null) {
    const data = await gql(
      `query Plants($businessUnitId: Int) {
        plants(businessUnitId: $businessUnitId) {
          id name businessUnitId
        }
      }`,
      { businessUnitId },
    );
    return data.plants;
  },

  async list() {
    const data = await gql(`
      query {
        inspectionK3lList {
          id tanggal kategoriTemuan deskripsiTemuan
          fotoSebelum fotoSesudah lokasi
          tindakanPerbaikan targetSelesai
          status aktualClose
          businessUnitId plantId departmentId
          createdAt updatedAt commentCount
        }
      }
    `);
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
          createdAt updatedAt commentCount
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
        $departmentId: Int
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
          departmentId: $departmentId
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
        $departmentId: Int
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
          departmentId: $departmentId
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
    return result;
  },
};
