import { createApp } from "vue";
import "./style.css";
import App from "./App.vue";
import router from "./router/routes";

const app = createApp(App);
app.use(router);
app.mount("#app");

// Register the service worker so the app is installable as a PWA and works
// offline. (Push notifications reuse this same registration.)
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js").catch(() => {
      /* registration failed (e.g. unsupported context) — app still works */
    });
  });
}
