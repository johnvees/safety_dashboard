import { createRouter, createWebHistory } from "vue-router";
import Login from "../login/Login.vue";
import Register from "../login/Register.vue";
import { authService } from "../services/authService.js";
import Dashboard from "../dashboard/Dashboard.vue";
import DashboardHome from "../dashboard/views/DashboardHome.vue";
import SafetyModules from "../dashboard/views/SafetyModules.vue";
import InspectionK3L from "../dashboard/views/InspectionK3L.vue";
import HseDailyReport from "../dashboard/views/HseDailyReport.vue";
import MasterData from "../dashboard/views/MasterData.vue";
import Settings from "../dashboard/views/Settings.vue";
import Chat from "../dashboard/views/Chat.vue";

const routes = [
  { path: "/", redirect: "/login" },
  { path: "/login", name: "Login", component: Login },
  { path: "/register", name: "Register", component: Register },
  {
    path: "/dashboard",
    component: Dashboard,
    meta: { requiresAuth: true },
    children: [
      { path: "", name: "DashboardHome", component: DashboardHome },
      { path: "modules", name: "SafetyModules", component: SafetyModules },
      { path: "reports", redirect: "/dashboard/reports/inspection-k3l" },
      {
        path: "reports/inspection-k3l",
        name: "InspectionK3L",
        component: InspectionK3L,
      },
      {
        path: "reports/hse-daily",
        name: "HseDailyReport",
        component: HseDailyReport,
      },
{ path: "chat", name: "Chat", component: Chat },
{ path: "master-data", name: "MasterData", component: MasterData },
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

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem("token");
  const expired = token && authService.isTokenExpired();

  if (expired) {
    authService.logout();
    return next({ name: "Login" });
  }

  if (to.meta.requiresAuth && !token) {
    next({ name: "Login" });
  } else if ((to.name === "Login" || to.name === "Register") && token) {
    next({ name: "DashboardHome" });
  } else {
    next();
  }
});

export default router;
