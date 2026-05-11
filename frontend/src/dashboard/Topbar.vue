<template>
  <header class="topbar">
    <div class="topbar-left">
      <button class="btn-hamburger" @click="emit('toggle-sidebar')" aria-label="Toggle sidebar">
        <span></span><span></span><span></span>
      </button>
      <div class="page-title">{{ title }}</div>
    </div>
    <div class="topbar-right">
      <div class="user-info">
        <div class="avatar">{{ initials }}</div>
        <div class="user-details">
          <span class="user-email">{{ user?.email }}</span>
          <span class="user-meta">{{ user?.role || 'user' }} · {{ user?.businessUnit || '-' }}</span>
        </div>
      </div>
      <button class="btn-logout" @click="handleLogout">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
          <polyline points="16 17 21 12 16 7"/>
          <line x1="21" y1="12" x2="9" y2="12"/>
        </svg>
        Logout
      </button>
    </div>
  </header>
</template>

<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";
import { authService } from "@/services/authService";

const props = defineProps({
  title: { type: String, default: "Dashboard" },
});

const emit = defineEmits(["toggle-sidebar"]);

const router = useRouter();
const user = authService.getCurrentUser();
const initials = computed(() =>
  user?.email ? user.email[0].toUpperCase() : "U",
);

const handleLogout = () => {
  authService.logout();
  router.push("/login");
};
</script>

<style scoped>
.topbar {
  height: 60px;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  flex-shrink: 0;
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-hamburger {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 5px;
  width: 32px;
  height: 32px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  transition: background 0.15s;
}

.btn-hamburger:hover {
  background: #f1f5f9;
}

.btn-hamburger span {
  display: block;
  height: 2px;
  width: 100%;
  background: #475569;
  border-radius: 2px;
  transition: background 0.15s;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: #3b82f6;
  color: #fff;
  font-size: 14px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-details {
  display: flex;
  flex-direction: column;
  line-height: 1.3;
}

.user-email {
  font-size: 14px;
  color: #475569;
}

.user-meta {
  font-size: 12px;
  color: #94a3b8;
  text-transform: capitalize;
}

.btn-logout {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  border: 1px solid #e5e7eb;
  border-radius: 7px;
  background: #fff;
  color: #64748b;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}

.btn-logout:hover {
  background: #fee2e2;
  color: #dc2626;
  border-color: #fca5a5;
}

.btn-logout svg {
  width: 15px;
  height: 15px;
}
</style>
