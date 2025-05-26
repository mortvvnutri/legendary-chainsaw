import { createRouter, createWebHistory } from "vue-router";
import { authGuard, adminGuard } from "./guard";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/auth",
      name: "Auth",
      component: () => import("../pages/AuthPage.vue"),
    },
    {
      path: "/",
      name: "Dashboard",
      component: () => import("../pages/DashboardPage.vue"),
    },
    {
      path: "/team",
      name: "TeamLK",
      component: () => import("../pages/TeamLK.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/admin",
      name: "Admin",
      component: () => import("../pages/Admin/AdminDashboard.vue"),
      beforeEnter: adminGuard,
      children: [
        {
          path: "tasks",
          name: "AdminTasks",
          component: () => import("../pages/Admin/AdminTasks.vue"),
        },
        {
          path: "tasks/new",
          name: "AdminTaskForm",
          component: () => import("../pages/Admin/AdminTaskForm.vue"),
        },
        {
          path: "solutions",
          name: "AdminSolutions",
          component: () => import("../pages/Admin/AdminSolutions.vue"),
        },
      ],
    },
  ],
});

router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem("token");

  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ path: "/auth", query: { redirect: to.fullPath } });
  } else if (isAuthenticated && to.path === "/auth") {
    next("/team");
  } else {
    next();
  }
});

export default router;
