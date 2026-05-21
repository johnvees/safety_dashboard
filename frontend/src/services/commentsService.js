const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
const GRAPHQL_URL = `${API_BASE}/graphql`;

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

const COMMENT_FIELDS = `
  id reportType reportId userId
  userEmail userFullName userUsername
  content createdAt updatedAt
  canEdit canDelete
`;

export const commentsService = {
  async list(reportType, reportId) {
    const data = await gql(
      `query Comments($reportType: String!, $reportId: Int!) {
        comments(reportType: $reportType, reportId: $reportId) { ${COMMENT_FIELDS} }
      }`,
      { reportType, reportId },
    );
    return data.comments;
  },

  async create(reportType, reportId, content) {
    const data = await gql(
      `mutation CreateComment($reportType: String!, $reportId: Int!, $content: String!) {
        createComment(reportType: $reportType, reportId: $reportId, content: $content) {
          success message
          comment { ${COMMENT_FIELDS} }
        }
      }`,
      { reportType, reportId, content },
    );
    const result = data.createComment;
    if (!result.success) throw new Error(result.message);
    return result.comment;
  },

  async update(id, content) {
    const data = await gql(
      `mutation UpdateComment($id: Int!, $content: String!) {
        updateComment(id: $id, content: $content) {
          success message
          comment { ${COMMENT_FIELDS} }
        }
      }`,
      { id, content },
    );
    const result = data.updateComment;
    if (!result.success) throw new Error(result.message);
    return result.comment;
  },

  async delete(id) {
    const data = await gql(
      `mutation DeleteComment($id: Int!) {
        deleteComment(id: $id) { success message }
      }`,
      { id },
    );
    const result = data.deleteComment;
    if (!result.success) throw new Error(result.message);
    return result;
  },
};
