import { createRouter, createWebHistory } from 'vue-router';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: () => import('../pages/AuthPage.vue')
    },
    // {
    //   path: '/dashboard',
    //   component: () => import('./views/DashboardView.vue'),
    //   meta: { requiresAuth: true }
    // },
    // другие маршруты
  ]
});

// Навигационный guard для проверки аутентификации
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('isAuthenticated');
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login');
  } else {
    next();
  }
});

export default router;