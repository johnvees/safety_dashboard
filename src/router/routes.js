import { createRouter, createWebHistory } from "vue-router";
import Login from "../login/Login.vue";
import Register from "../login/Register.vue";
import Dashboard from "../dashboard/Dashboard.vue";
import SafetyModules from "../dashboard/views/SafetyModules.vue";
import InspectionK3L from "../dashboard/views/InspectionK3L.vue";

const routes = [
  { path: "/", redirect: "/login" },
  { path: "/login", name: "Login", component: Login },
  { path: "/register", name: "Register", component: Register },
  {
    path: "/dashboard",
    component: Dashboard,
    children: [
      { path: "", redirect: "/dashboard/modules" },
      { path: "modules", name: "SafetyModules", component: SafetyModules },
      { path: "reports", redirect: "/dashboard/reports/inspection-k3l" },
      { path: "reports/inspection-k3l", name: "InspectionK3L", component: InspectionK3L },
      { path: "settings", name: "Settings", component: { template: "<div style='padding:32px'><h2>Settings coming soon</h2></div>" } },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
