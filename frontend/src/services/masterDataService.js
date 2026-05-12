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

export const masterDataService = {
  // ── Business Unit ─────────────────────────────────────────────────────

  async listBusinessUnits() {
    const data = await gql(`
      query {
        businessUnits {
          id name code description isActive createdAt
        }
      }
    `);
    return data.businessUnits;
  },

  async createBusinessUnit(input) {
    const data = await gql(
      `mutation CreateBU($name: String!, $code: String!, $description: String, $isActive: Boolean) {
        createBusinessUnit(name: $name, code: $code, description: $description, isActive: $isActive) {
          success message
          businessUnit { id name code description isActive createdAt }
        }
      }`,
      input,
    );
    const r = data.createBusinessUnit;
    if (!r.success) throw new Error(r.message);
    return r;
  },

  async updateBusinessUnit(id, input) {
    const data = await gql(
      `mutation UpdateBU($id: Int!, $name: String, $code: String, $description: String, $isActive: Boolean) {
        updateBusinessUnit(id: $id, name: $name, code: $code, description: $description, isActive: $isActive) {
          success message
          businessUnit { id name code description isActive createdAt }
        }
      }`,
      { id, ...input },
    );
    const r = data.updateBusinessUnit;
    if (!r.success) throw new Error(r.message);
    return r;
  },

  async deleteBusinessUnit(id) {
    const data = await gql(
      `mutation DeleteBU($id: Int!) {
        deleteBusinessUnit(id: $id) { success message }
      }`,
      { id },
    );
    const r = data.deleteBusinessUnit;
    if (!r.success) throw new Error(r.message);
    return r;
  },

  // ── Plant ─────────────────────────────────────────────────────────────

  async listPlants(businessUnitId = null) {
    const data = await gql(
      `query Plants($businessUnitId: Int) {
        plants(businessUnitId: $businessUnitId) {
          id name code businessUnitId location isActive createdAt
        }
      }`,
      { businessUnitId },
    );
    return data.plants;
  },

  async createPlant(input) {
    const data = await gql(
      `mutation CreatePlant($name: String!, $code: String!, $businessUnitId: Int!, $location: String, $isActive: Boolean) {
        createPlant(name: $name, code: $code, businessUnitId: $businessUnitId, location: $location, isActive: $isActive) {
          success message
          plant { id name code businessUnitId location isActive createdAt }
        }
      }`,
      input,
    );
    const r = data.createPlant;
    if (!r.success) throw new Error(r.message);
    return r;
  },

  async updatePlant(id, input) {
    const data = await gql(
      `mutation UpdatePlant($id: Int!, $name: String, $code: String, $businessUnitId: Int, $location: String, $isActive: Boolean) {
        updatePlant(id: $id, name: $name, code: $code, businessUnitId: $businessUnitId, location: $location, isActive: $isActive) {
          success message
          plant { id name code businessUnitId location isActive createdAt }
        }
      }`,
      { id, ...input },
    );
    const r = data.updatePlant;
    if (!r.success) throw new Error(r.message);
    return r;
  },

  async deletePlant(id) {
    const data = await gql(
      `mutation DeletePlant($id: Int!) {
        deletePlant(id: $id) { success message }
      }`,
      { id },
    );
    const r = data.deletePlant;
    if (!r.success) throw new Error(r.message);
    return r;
  },

  // ── Roles ─────────────────────────────────────────────────────────────

  async listRoles() {
    const data = await gql(`
      query {
        roles { id name level description }
      }
    `);
    return data.roles;
  },

  async createRole(input) {
    const data = await gql(
      `mutation CreateRole($name: String!, $level: Int!, $description: String) {
        createRole(name: $name, level: $level, description: $description) {
          success message
          role { id name level description }
        }
      }`,
      input,
    );
    const r = data.createRole;
    if (!r.success) throw new Error(r.message);
    return r;
  },

  async updateRole(id, input) {
    const data = await gql(
      `mutation UpdateRole($id: Int!, $name: String, $level: Int, $description: String) {
        updateRole(id: $id, name: $name, level: $level, description: $description) {
          success message
          role { id name level description }
        }
      }`,
      { id, ...input },
    );
    const r = data.updateRole;
    if (!r.success) throw new Error(r.message);
    return r;
  },

  async deleteRole(id) {
    const data = await gql(
      `mutation DeleteRole($id: Int!) {
        deleteRole(id: $id) { success message }
      }`,
      { id },
    );
    const r = data.deleteRole;
    if (!r.success) throw new Error(r.message);
    return r;
  },

  // ── Users ─────────────────────────────────────────────────────────────

  async listUsers() {
    const data = await gql(`
      query {
        users { id email username fullName roleId businessUnitId plantId isActive createdAt updatedAt }
      }
    `);
    return data.users;
  },

  async createUser(input) {
    const data = await gql(
      `mutation CreateUser(
        $email: String!, $password: String!, $username: String, $fullName: String,
        $roleId: Int, $businessUnitId: Int, $plantId: Int, $isActive: Boolean
      ) {
        createUser(email: $email, password: $password, username: $username, fullName: $fullName,
          roleId: $roleId, businessUnitId: $businessUnitId, plantId: $plantId, isActive: $isActive) {
          success message
          user { id email username fullName roleId businessUnitId plantId isActive createdAt }
        }
      }`,
      input,
    );
    const r = data.createUser;
    if (!r.success) throw new Error(r.message);
    return r;
  },

  async updateUser(id, input) {
    const data = await gql(
      `mutation UpdateUser(
        $id: Int!, $email: String, $password: String, $username: String, $fullName: String,
        $roleId: Int, $businessUnitId: Int, $plantId: Int, $isActive: Boolean
      ) {
        updateUser(id: $id, email: $email, password: $password, username: $username, fullName: $fullName,
          roleId: $roleId, businessUnitId: $businessUnitId, plantId: $plantId, isActive: $isActive) {
          success message
          user { id email username fullName roleId businessUnitId plantId isActive createdAt }
        }
      }`,
      { id, ...input },
    );
    const r = data.updateUser;
    if (!r.success) throw new Error(r.message);
    return r;
  },

  async deleteUser(id) {
    const data = await gql(
      `mutation DeleteUser($id: Int!) {
        deleteUser(id: $id) { success message }
      }`,
      { id },
    );
    const r = data.deleteUser;
    if (!r.success) throw new Error(r.message);
    return r;
  },
};
