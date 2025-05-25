import { createRouter, createWebHistory } from 'vue-router';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/auth',
      component: () => import('../pages/AuthPage.vue')
    },
    {
      path: '/',
      component: () => import('../pages/DashboardPage.vue'),
      meta: { requiresAuth: true }
    },
    // другие маршруты
  ]
});

// Навигационный guard для проверки аутентификации
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('token');
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/auth');
  } else {
    next();
  }
});

export default router;