import { createRouter, createWebHistory } from "vue-router";
import Login from "../login/Login.vue";
import { authService } from "../services/authService.js";
import Dashboard from "../dashboard/Dashboard.vue";
import DashboardHome from "../dashboard/views/DashboardHome.vue";
import SafetyModules from "../dashboard/views/SafetyModules.vue";
import InspectionK3L from "../dashboard/views/InspectionK3L.vue";
import PermitKerjaHSE from "../dashboard/views/PermitKerjaHSE.vue";
import CaseIncident from "../dashboard/views/CaseIncident.vue";
import MasterData from "../dashboard/views/MasterData.vue";
import Settings from "../dashboard/views/Settings.vue";
import Chat from "../dashboard/views/Chat.vue";

const routes = [
  { path: "/", redirect: "/login" },
  { path: "/login", name: "Login", component: Login },
  { path: "/register", redirect: "/login" },
  {
    path: "/dashboard",
    component: Dashboard,
    meta: { requiresAuth: true },
    children: [
      { path: "", name: "DashboardHome", component: DashboardHome },
      { path: "modules", redirect: "/dashboard/modules/sop" },
      {
        path: "modules/sop",
        name: "ModulSoP",
        component: SafetyModules,
        props: { kategori: "SoP", pageTitle: "Standard of Procedure (SoP)" },
      },
      {
        path: "modules/wi",
        name: "ModulWI",
        component: SafetyModules,
        props: { kategori: "WI", pageTitle: "Working Instruction (WI)" },
      },
      {
        path: "modules/form",
        name: "ModulForm",
        component: SafetyModules,
        props: { kategori: "Form", pageTitle: "Form" },
      },
      {
        path: "modules/edukasi",
        name: "ModulEdukasi",
        component: SafetyModules,
        props: { kategori: "Safety Sharing", pageTitle: "Safety Sharing (Edukasi)" },
      },
      { path: "reports", redirect: "/dashboard/reports/inspection-k3l" },
      {
        path: "reports/inspection-k3l",
        name: "InspectionK3L",
        component: InspectionK3L,
      },
      {
        path: "reports/hse-daily",
        name: "PermitKerjaHSE",
        component: PermitKerjaHSE,
      },
      {
        path: "reports/case-incident",
        name: "CaseIncident",
        component: CaseIncident,
      },
{ path: "chat", name: "Chat", component: Chat },
{ path: "master-data", name: "MasterData", component: MasterData, meta: { requiresAdmin: true } },
      {
        path: "settings",
        name: "Settings",
        component: Settings,
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, _from) => {
  const token = localStorage.getItem("token");
  const expired = token && authService.isTokenExpired();

  if (expired) {
    authService.logout();
    return { name: "Login" };
  }

  if (to.meta.requiresAuth && !token) {
    return { name: "Login" };
  }

  if (to.name === "Login" && token) {
    return { name: "DashboardHome" };
  }

  if (to.meta.requiresAdmin && !authService.canAccessMasterData()) {
    return { name: "DashboardHome" };
  }
});

export default router;
