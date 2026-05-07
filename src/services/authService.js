const GRAPHQL_URL = "http://localhost:8000/graphql";

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

export const authService = {
  async register(email, password) {
    const data = await gql(
      `mutation Register($email: String!, $password: String!) {
        register(email: $email, password: $password) {
          success message token
          user { id email role businessUnit }
        }
      }`,
      { email, password },
    );
    const result = data.register;
    if (!result.success) throw new Error(result.message);
    localStorage.setItem("token", result.token);
    localStorage.setItem("user", JSON.stringify(result.user));
    return result;
  },

  async login(email, password) {
    const data = await gql(
      `mutation Login($email: String!, $password: String!) {
        login(email: $email, password: $password) {
          success message token
          user { id email role businessUnit }
        }
      }`,
      { email, password },
    );
    const result = data.login;
    if (!result.success) throw new Error(result.message);
    localStorage.setItem("token", result.token);
    localStorage.setItem("user", JSON.stringify(result.user));
    return result;
  },

  getCurrentUser() {
    const raw = localStorage.getItem("user");
    return raw ? JSON.parse(raw) : null;
  },

  logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
  },
};
