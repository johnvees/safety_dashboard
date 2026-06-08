import { makeCache } from '@/utils/apiCache.js';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
const GRAPHQL_URL = `${API_BASE}/graphql`;
const UPLOAD_VIDEO_URL = `${API_BASE}/upload-video`;
const UPLOAD_DOC_URL = `${API_BASE}/upload-document`;

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

async function uploadToEndpoint(url, file) {
  const token = localStorage.getItem("token");
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(url, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Upload failed: ${res.status}`);
  }

  const { url: fileUrl } = await res.json();
  return fileUrl;
}

export function getMediaType(file) {
  if (file.type.startsWith("video/")) return "video";
  if (file.type.startsWith("image/")) return "image";
  return "document";
}

export async function uploadVideo(file) {
  return uploadToEndpoint(UPLOAD_VIDEO_URL, file);
}

export async function uploadImage(file) {
  const token = localStorage.getItem("token");
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/upload`, {
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

export async function uploadDocument(file) {
  return uploadToEndpoint(UPLOAD_DOC_URL, file);
}

export async function uploadFile(file) {
  const type = getMediaType(file);
  if (type === "video") return { url: await uploadVideo(file), mediaType: "video" };
  if (type === "image") return { url: await uploadImage(file), mediaType: "image" };
  return { url: await uploadDocument(file), mediaType: "document" };
}

export const safetyModulesService = {
  async list() {
    const hit = _cache.get('list');
    if (hit) return hit;
    const data = await gql(`
      query {
        safetyModules {
          id title videoUrl mediaType files kategori peraturan description createdBy createdAt updatedAt
        }
      }
    `);
    _cache.set('list', data.safetyModules);
    return data.safetyModules;
  },

  async create(title, files, description = null, peraturan = null, kategori = null) {
    const filesJson = JSON.stringify(files);
    const first = files[0] ?? {};
    const data = await gql(
      `mutation CreateSafetyModule($title: String!, $videoUrl: String, $mediaType: String, $files: String, $kategori: String, $peraturan: String, $description: String) {
        createSafetyModule(title: $title, videoUrl: $videoUrl, mediaType: $mediaType, files: $files, kategori: $kategori, peraturan: $peraturan, description: $description) {
          success message
          module { id title videoUrl mediaType files kategori peraturan description createdAt }
        }
      }`,
      { title, videoUrl: first.url ?? null, mediaType: first.mediaType ?? "video", files: filesJson, kategori, peraturan, description },
    );
    const result = data.createSafetyModule;
    if (!result.success) throw new Error(result.message);
    _cache.del('list');
    return result.module;
  },

  async update(id, title, files, description, peraturan, kategori) {
    const filesJson = JSON.stringify(files);
    const first = files[0] ?? {};
    const data = await gql(
      `mutation UpdateSafetyModule($id: Int!, $title: String, $videoUrl: String, $mediaType: String, $files: String, $kategori: String, $peraturan: String, $description: String) {
        updateSafetyModule(id: $id, title: $title, videoUrl: $videoUrl, mediaType: $mediaType, files: $files, kategori: $kategori, peraturan: $peraturan, description: $description) {
          success message
          module { id title videoUrl mediaType files kategori peraturan description createdAt }
        }
      }`,
      { id, title, videoUrl: first.url ?? null, mediaType: first.mediaType ?? "video", files: filesJson, kategori: kategori || "", peraturan: peraturan || "", description: description || "" },
    );
    const result = data.updateSafetyModule;
    if (!result.success) throw new Error(result.message);
    _cache.del('list');
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
    _cache.del('list');
    return result;
  },
};
