<template>
  <div class="bg-gray-800 rounded-lg shadow-lg p-6">
    <h2 class="text-2xl font-bold mb-6">Список задач</h2>

    <!-- Таблица -->
    <div class="overflow-x-auto">
      <table class="w-full table-auto border-collapse">
        <thead>
          <tr class="bg-gray-700 text-sm uppercase text-left">
            <th class="px-4 py-3">ID</th>
            <th class="px-4 py-3">Вопрос</th>
            <!-- Пустой столбец для визуального разделения -->
            <th class="px-4 py-3" style="width: 1px"></th>
            <th class="px-4 py-3">Тип ошибки</th>
            <th class="px-4 py-3">Позиция</th>
            <th class="px-4 py-3">Дата создания</th>
            <th class="px-4 py-3 text-right">Действия</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-700">
          <tr
            v-for="task in tasks"
            :key="task.task_id"
            class="hover:bg-gray-700 transition-colors"
          >
            <td class="px-4 py-3">{{ task.task_id }}</td>

            <td class="px-4 py-3 max-w-xs truncate">
              <span class="font-medium">{{ task.question }}</span>
            </td>

            <!-- Пустая ячейка для визуального разделения -->
            <td class="px-4 py-3" style="width: 1px"></td>

            <!-- Тип ошибки -->
            <td class="px-4 py-3">
              <div v-if="task.answer?.selections?.[0]?.type" class="text-sm">
                {{ task.answer.selections[0].type }}
              </div>
              <span v-else class="text-gray-500">—</span>
            </td>

            <!-- Позиция выделения -->
            <td class="px-4 py-3">
              <div v-if="task.answer?.selections?.[0]" class="text-sm">
                {{ task.answer.selections[0].startSelection }}–{{
                  task.answer.selections[0].endSelection
                }}
              </div>
              <span v-else class="text-gray-500">—</span>
            </td>

            <!-- Дата создания -->
            <td class="px-4 py-3 text-sm text-gray-400">
              {{ formatDate(task.created_at) }}
            </td>

            <!-- Действия -->
            <td class="px-4 py-3 text-right space-x-2">
              <button
                @click="editTask(task)"
                class="text-blue-400 hover:text-blue-300"
              >
                Редактировать
              </button>
              <button
                @click="deleteTask(task)"
                class="text-red-400 hover:text-red-300"
              >
                Удалить
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "@/services/api";

const tasks = ref([]);

// Формат даты
const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleString("ru-RU", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
};

onMounted(async () => {
  try {
    const data = await api.admin.getAdminTasks();
    tasks.value = data;
  } catch (err) {
    console.error("Ошибка загрузки задач", err);
  }
});
</script>
