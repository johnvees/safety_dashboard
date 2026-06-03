<template>
  <div class="register-container">
    <div class="register-card">
      <h1>Daftar</h1>

      <div v-if="error" class="error-alert">{{ error }}</div>
      <div v-if="successMessage" class="success-alert">{{ successMessage }}</div>

      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="email">Email:</label>
          <input
            id="email"
            v-model="email"
            type="email"
            placeholder="Masukkan email Anda (@cp.co.id)"
            required
            @blur="validateEmail"
          />
          <span v-if="emailError" class="error-message">{{ emailError }}</span>
        </div>
        <div class="form-group">
          <label for="password">Password:</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="Minimal 6 karakter"
            required
          />
        </div>
        <button type="submit" class="btn-register" :disabled="!!emailError || loading">
          {{ loading ? "Mendaftar..." : "Daftar" }}
        </button>
      </form>

      <p class="login-link">
        Sudah punya akun?
        <router-link to="/login">Login di sini</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { authService } from "@/services/authService";

const router = useRouter();
const email = ref("");
const password = ref("");
const emailError = ref("");
const loading = ref(false);
const error = ref("");
const successMessage = ref("");

const validateEmail = () => {
  emailError.value =
    email.value && !email.value.endsWith("@cp.co.id")
      ? "Email harus berakhiran @cp.co.id"
      : "";
};

const handleRegister = async () => {
  error.value = "";
  successMessage.value = "";
  loading.value = true;
  try {
    validateEmail();
    if (emailError.value) throw new Error(emailError.value);
    if (password.value.length < 6) throw new Error("Password minimal 6 karakter");

    await authService.register(email.value, password.value);
    router.push("/dashboard");
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.register-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-image: url("@/assets/cpbg.png");
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

.register-card {
  background: rgba(255, 255, 255, 0.95);
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 400px;
}

.register-card h1 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
  font-size: 28px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #555;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 14px;
  box-sizing: border-box;
  transition: border-color 0.3s;
  background-color: #fff;
  color: #333;
}

.form-group input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 5px rgba(59, 130, 246, 0.3);
}

.error-message {
  color: #f44336;
  font-size: 12px;
  margin-top: 5px;
  display: block;
}

.error-alert {
  background-color: #f8d7da;
  color: #721c24;
  padding: 12px;
  border-radius: 5px;
  margin-bottom: 15px;
  border: 1px solid #f5c6cb;
  font-size: 14px;
}

.success-alert {
  background-color: #d4edda;
  color: #155724;
  padding: 12px;
  border-radius: 5px;
  margin-bottom: 15px;
  border: 1px solid #c3e6cb;
  font-size: 14px;
}

.btn-register {
  width: 100%;
  padding: 12px;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-register:hover:not(:disabled) {
  background-color: #2563eb;
}

.btn-register:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.login-link {
  text-align: center;
  margin-top: 20px;
  color: #666;
  font-size: 14px;
}

.login-link a {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 600;
}

.login-link a:hover {
  text-decoration: underline;
}
</style>
