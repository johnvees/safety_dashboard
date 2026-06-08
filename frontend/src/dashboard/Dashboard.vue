<template>
  <div class="layout">
    <Sidebar :open="sidebarOpen" />
    <div
      v-if="sidebarOpen"
      class="sidebar-backdrop"
      @click="sidebarOpen = false"
    />
    <div class="main">
      <Topbar :title="pageTitle" @toggle-sidebar="sidebarOpen = !sidebarOpen" />
      <div class="content">
        <router-view v-slot="{ Component }">
          <keep-alive>
            <component :is="Component" />
          </keep-alive>
        </router-view>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useRoute } from "vue-router";
import Sidebar from "./Sidebar.vue";
import Topbar from "./Topbar.vue";

const sidebarOpen = ref(window.innerWidth >= 768);

const route = useRoute();
const pageTitles = {
  "/dashboard": "Dashboard",
  "/dashboard/modules/sop": "Modul HSE - Standard of Procedure (SoP)",
  "/dashboard/modules/wi": "Modul HSE - Working Instruction (WI)",
  "/dashboard/modules/form": "Modul HSE - Form",
  "/dashboard/modules/edukasi": "Modul HSE - Safety Sharing (Edukasi)",
  "/dashboard/reports": "Laporan",
  "/dashboard/reports/inspection-k3l": "Inspection K3L",
  "/dashboard/reports/hse-daily": "HSE Daily Report",
  "/dashboard/chat": "Chat",
  "/dashboard/master-data": "Master Data",
  "/dashboard/settings": "Pengaturan",
};
const pageTitle = computed(() => pageTitles[route.path] ?? "Dashboard");
</script>

<style scoped>
.layout {
  display: flex;
  height: 100vh; /* fallback for old browsers */
  height: 100dvh; /* dynamic viewport: fits the visible area as mobile browser bars show/hide */
  overflow: hidden;
  background: #f1f5f9;
}

.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  width: 100%;
  overflow: hidden;
}

.content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

/* Backdrop — only visible/interactive on mobile */
.sidebar-backdrop {
  display: none;
}

@media (max-width: 767px) {
  .sidebar-backdrop {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(15, 23, 42, 0.45);
    z-index: 199;
  }
}
</style>
