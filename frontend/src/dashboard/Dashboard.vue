<template>
  <div class="layout">
    <Sidebar />
    <div class="main">
      <Topbar :title="pageTitle" />
      <div class="content">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";
import Sidebar from "./Sidebar.vue";
import Topbar from "./Topbar.vue";

const route = useRoute();
const pageTitles = {
  "/dashboard": "Dashboard",
  "/dashboard/modules": "Safety Modules",
  "/dashboard/reports": "Reports",
  "/dashboard/reports/inspection-k3l": "Inspection K3L",
  "/dashboard/settings": "Settings",
};
const pageTitle = computed(() => pageTitles[route.path] ?? "Dashboard");
</script>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
  background: #f1f5f9;
}

.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.content {
  flex: 1;
  overflow-y: auto;
}
</style>
