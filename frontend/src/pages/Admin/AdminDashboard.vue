<template>
  <div class="min-h-screen bg-gray-900 text-white">
    <!-- Навигационное меню -->
    <aside class="bg-gray-800 w-64 fixed h-full">
      <div class="p-6">
        <h1 class="text-xl font-bold mb-6">Админ-панель</h1>
        <nav class="space-y-2">
          <router-link
            to="/admin/tasks"
            class="block py-2 px-4 rounded hover:bg-gray-700"
          >
            Задачи
          </router-link>
          <router-link
            to="/admin/solutions"
            class="block py-2 px-4 rounded hover:bg-gray-700"
          >
            Решения
          </router-link>
        </nav>
      </div>
    </aside>

    <!-- Основной контент -->
    <main class="ml-64 p-6">
      <router-view />
    </main>
  </div>
</template>
