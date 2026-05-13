const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
const GRAPHQL_URL = `${API_BASE}/graphql`;
const UPLOAD_VIDEO_URL = `${API_BASE}/upload-video`;

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

export async function uploadVideo(file) {
  const token = localStorage.getItem("token");
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(UPLOAD_VIDEO_URL, {
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

export const safetyModulesService = {
  async list() {
    const data = await gql(`
      query {
        safetyModules {
          id title videoUrl description createdBy createdAt updatedAt
        }
      }
    `);
    return data.safetyModules;
  },

  async create(title, videoUrl, description = null) {
    const data = await gql(
      `mutation CreateSafetyModule($title: String!, $videoUrl: String, $description: String) {
        createSafetyModule(title: $title, videoUrl: $videoUrl, description: $description) {
          success message
          module { id title videoUrl description createdAt }
        }
      }`,
      { title, videoUrl, description },
    );
    const result = data.createSafetyModule;
    if (!result.success) throw new Error(result.message);
    return result.module;
  },

  async delete(id) {
    const data = await gql(
      `mutation DeleteSafetyModule($id: Int!) {
        deleteSafetyModule(id: $id) {
          success message
        }
      }`,
      { id },
    );
    const result = data.deleteSafetyModule;
    if (!result.success) throw new Error(result.message);
    return result;
  },
};
