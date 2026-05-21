import { createClient } from "graphql-ws";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
const GRAPHQL_URL = `${API_BASE}/graphql`;
const WS_URL = GRAPHQL_URL.replace(/^http/, "ws");
const CHAT_UPLOAD_URL = `${API_BASE}/upload-chat-media`;

export async function uploadChatMedia(file) {
  const token = localStorage.getItem("token");
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(CHAT_UPLOAD_URL, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Upload gagal: ${res.status}`);
  }
  return res.json(); // { url, type }
}

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

const MESSAGE_FIELDS = `
  id senderId recipientId content
  attachmentUrl attachmentType
  createdAt updatedAt readAt
  senderFullName senderEmail senderUsername
`;

const USER_SUMMARY_FIELDS = `
  id email fullName username
  roleId roleName roleLevel
  businessUnitId businessUnitName
  plantId plantName isActive
  lastMessageContent lastMessageAt lastMessageFromMe unreadCount
`;

export const chatService = {
  async listUsers() {
    const data = await gql(`query { chatUsers { ${USER_SUMMARY_FIELDS} } }`);
    return data.chatUsers;
  },

  async listMessages(otherUserId, { limit = 100, beforeId = null } = {}) {
    const data = await gql(
      `query Messages($otherUserId: Int!, $limit: Int, $beforeId: Int) {
        chatMessages(otherUserId: $otherUserId, limit: $limit, beforeId: $beforeId) {
          ${MESSAGE_FIELDS}
        }
      }`,
      { otherUserId, limit, beforeId },
    );
    return data.chatMessages;
  },

  async sendMessage(recipientId, { content = null, attachmentUrl = null, attachmentType = null } = {}) {
    const data = await gql(
      `mutation SendMessage($recipientId: Int!, $content: String, $attachmentUrl: String, $attachmentType: String) {
        sendChatMessage(recipientId: $recipientId, content: $content, attachmentUrl: $attachmentUrl, attachmentType: $attachmentType) {
          success message
          chatMessage { ${MESSAGE_FIELDS} }
        }
      }`,
      { recipientId, content, attachmentUrl, attachmentType },
    );
    const result = data.sendChatMessage;
    if (!result.success) throw new Error(result.message);
    return result.chatMessage;
  },

  async updateMessage(id, content) {
    const data = await gql(
      `mutation UpdateChatMessage($id: Int!, $content: String!) {
        updateChatMessage(id: $id, content: $content) {
          success message
          chatMessage { ${MESSAGE_FIELDS} }
        }
      }`,
      { id, content },
    );
    const result = data.updateChatMessage;
    if (!result.success) throw new Error(result.message);
    return result.chatMessage;
  },

  async deleteMessage(id) {
    const data = await gql(
      `mutation DeleteChatMessage($id: Int!) {
        deleteChatMessage(id: $id) { success message }
      }`,
      { id },
    );
    const result = data.deleteChatMessage;
    if (!result.success) throw new Error(result.message);
    return result;
  },

  async markRead(otherUserId) {
    const data = await gql(
      `mutation MarkRead($otherUserId: Int!) {
        markChatRead(otherUserId: $otherUserId) { success message }
      }`,
      { otherUserId },
    );
    return data.markChatRead;
  },
};

// ── Subscription client ────────────────────────────────────────────────────
let _wsClient = null;

function getWsClient() {
  if (_wsClient) return _wsClient;
  _wsClient = createClient({
    url: WS_URL,
    lazy: true,
    retryAttempts: 8,
    keepAlive: 20_000,
    connectionParams: () => {
      const token = localStorage.getItem("token");
      return token ? { authorization: `Bearer ${token}` } : {};
    },
  });
  return _wsClient;
}

export function subscribeToMessages({ onMessage, onError } = {}) {
  const client = getWsClient();
  const unsubscribe = client.subscribe(
    {
      query: `subscription { chatMessageStream { ${MESSAGE_FIELDS} } }`,
    },
    {
      next: (payload) => {
        const msg = payload?.data?.chatMessageStream;
        if (msg && typeof onMessage === "function") onMessage(msg);
      },
      error: (err) => {
        if (typeof onError === "function") onError(err);
      },
      complete: () => {},
    },
  );
  return unsubscribe;
}

export function disposeChatSocket() {
  if (_wsClient) {
    try { _wsClient.dispose(); } catch { /* ignore */ }
    _wsClient = null;
  }
}
