<template>
  <aside class="sidebar" :class="{ collapsed: !open }">
    <div class="brand">
      <img src="@/assets/CPIN.JK.png" alt="CP Logo" class="brand-logo" />
      <span class="brand-name">Safety Portal</span>
    </div>

    <nav class="nav">
      <router-link to="/dashboard" class="nav-item" exact-active-class="active">
        <svg
          class="nav-icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <rect x="3" y="3" width="7" height="7" rx="1" />
          <rect x="14" y="3" width="7" height="7" rx="1" />
          <rect x="3" y="14" width="7" height="7" rx="1" />
          <rect x="14" y="14" width="7" height="7" rx="1" />
        </svg>
        Dashboard
      </router-link>

      <router-link
        to="/dashboard/modules"
        class="nav-item"
        active-class="active"
      >
        <svg
          class="nav-icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path
            d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"
          />
          <polyline points="14 2 14 8 20 8" />
          <line x1="9" y1="13" x2="15" y2="13" />
          <line x1="9" y1="17" x2="15" y2="17" />
          <line x1="9" y1="9" x2="11" y2="9" />
        </svg>
        Safety Modules
      </router-link>

      <!-- Reports with submenu -->
      <div class="nav-group" :class="{ open: reportsOpen }">
        <div class="nav-item nav-parent" :class="{ active: isReportsActive }" @click="reportsOpen = !reportsOpen">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
          </svg>
          Reports
          <svg class="nav-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="6 9 12 15 18 9"/>
          </svg>
        </div>
        <div class="nav-submenu" v-show="reportsOpen">
          <router-link to="/dashboard/reports/inspection-k3l" class="nav-subitem" active-class="active">
            Inspection K3L
          </router-link>
          <router-link to="/dashboard/reports/hse-daily" class="nav-subitem" active-class="active">
            HSE Daily Report
          </router-link>
        </div>
      </div>

      <router-link
        to="/dashboard/chat"
        class="nav-item"
        active-class="active"
      >
        <svg
          class="nav-icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
        </svg>
        Chat
      </router-link>

      <router-link
        to="/dashboard/master-data"
        class="nav-item"
        active-class="active"
      >
        <svg
          class="nav-icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <ellipse cx="12" cy="5" rx="9" ry="3" />
          <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
          <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
        </svg>
        Master Data
      </router-link>

      <router-link
        to="/dashboard/settings"
        class="nav-item"
        active-class="active"
      >
        <svg
          class="nav-icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <circle cx="12" cy="12" r="3" />
          <path
            d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"
          />
        </svg>
        Settings
      </router-link>
    </nav>
  </aside>
</template>

<script setup>
import { ref, computed } from "vue";
import { useRoute } from "vue-router";

defineProps({ open: { type: Boolean, default: true } });

const route = useRoute();
const isReportsActive = computed(() => route.path.startsWith("/dashboard/reports"));
const reportsOpen = ref(isReportsActive.value);
</script>

<style scoped>
.sidebar {
  width: 240px;
  height: 100vh;
  background: #1e2a3a;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  overflow-y: auto;
  overflow-x: hidden;
  transition: width 0.25s ease;
}

.sidebar.collapsed {
  width: 0;
}

/* On mobile: sidebar floats over content, doesn't push layout */
@media (max-width: 767px) {
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    width: 240px;
    z-index: 200;
    transform: translateX(0);
    transition: transform 0.25s ease;
  }

  .sidebar.collapsed {
    width: 240px;
    transform: translateX(-100%);
  }
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.brand-logo {
  width: 36px;
  height: 36px;
  object-fit: contain;
  border-radius: 6px;
}

.brand-name {
  color: #fff;
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 0.3px;
}

.nav {
  padding: 12px 8px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  color: #94a3b8;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition:
    background 0.15s,
    color 0.15s;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.07);
  color: #e2e8f0;
}

.nav-item.active {
  background: #3b82f6;
  color: #fff;
}

.nav-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

/* Submenu styles */
.nav-group {
  display: flex;
  flex-direction: column;
}

.nav-parent {
  cursor: pointer;
  user-select: none;
}

.nav-chevron {
  width: 16px;
  height: 16px;
  margin-left: auto;
  transition: transform 0.2s;
}

.nav-group.open .nav-chevron {
  transform: rotate(180deg);
}

.nav-submenu {
  display: flex;
  flex-direction: column;
  gap: 1px;
  padding-left: 20px;
  margin-top: 2px;
}

.nav-subitem {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 6px;
  color: #94a3b8;
  text-decoration: none;
  font-size: 13px;
  font-weight: 500;
  transition: background 0.15s, color 0.15s;
}

.nav-subitem:hover {
  background: rgba(255,255,255,0.07);
  color: #e2e8f0;
}

.nav-subitem.active {
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
}
</style>
