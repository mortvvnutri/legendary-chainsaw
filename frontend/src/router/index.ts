// src/router/index.ts
import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/auth",
      component: () => import("../pages/AuthPage.vue"),
    },
    {
      path: "/",
      component: () => import("../pages/DashboardPage.vue"),
    },
    {
      path: "/team",
      component: () => import("../pages/TeamLK.vue"),
      meta: { requiresAuth: true },
    },
    // Дополнительные маршруты можно добавить здесь
  ],
});

router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem("token");

  if (to.meta.requiresAuth && !isAuthenticated) {
    // Если маршрут требует авторизации, а токена нет → /auth
    next({ path: "/auth", query: { redirect: to.fullPath } });
  } else if (isAuthenticated && to.path === "/auth") {
    // Если уже авторизован и пытается зайти на /auth → редирект на /team
    next("/team");
  } else {
    next();
  }
});
export default router;
