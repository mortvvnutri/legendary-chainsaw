<template>
  <div class="max-w-4xl mx-auto">
    <h2 class="text-2xl font-bold mb-6">Решения команды</h2>

    <!-- Форма ввода ID команды -->
    <div class="bg-gray-800 rounded-lg shadow-lg p-6 mb-6">
      <div class="flex space-x-4">
        <input
          v-model.number="filter.teamId"
          type="number"
          placeholder="Введите ID команды"
          class="bg-gray-700 p-2 border border-gray-600 rounded w-1/2"
        />
        <button
          @click="loadSolutions"
          :disabled="!filter.teamId || loading"
          class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded disabled:bg-blue-400 w-1/2"
        >
          {{ loading ? "Загрузка..." : "Загрузить решения" }}
        </button>
      </div>
    </div>

    <!-- Сообщения -->
    <div v-if="errorMessage" class="bg-red-900 text-red-100 p-4 rounded mb-6">
      {{ errorMessage }}
    </div>

    <!-- Список решений -->
    <div
      v-if="solutions.length && !loading"
      class="bg-gray-800 rounded-lg shadow-lg overflow-hidden"
    >
      <table class="w-full">
        <thead class="bg-gray-700">
          <tr>
            <th class="px-6 py-3 text-left">ID решения</th>
            <th class="px-6 py-3 text-left">Задача</th>
            <th class="px-6 py-3 text-left">Ответ</th>
            <th class="px-6 py-3 text-left">Статус</th>
            <th class="px-6 py-3 text-left">Дата отправки</th>
            <th class="px-6 py-3 text-left">Дата изменения</th>
            <th class="px-6 py-3 text-right">Действия</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-700">
          <tr
            v-for="solution in solutions"
            :key="solution.solution_id"
            class="hover:bg-gray-700 transition-colors"
          >
            <td class="px-6 py-4">{{ solution.solution_id }}</td>
            <td class="px-6 py-4">{{ solution.task_id }}</td>
            <td class="px-6 py-4">
              <div v-if="solution.answer?.selections?.length" class="space-y-1">
                <p>Тип: {{ solution.answer.selections[0].type }}</p>
                <p>
                  Позиция: {{ solution.answer.selections[0].startSelection }}–{{
                    solution.answer.selections[0].endSelection
                  }}
                </p>
              </div>
            </td>
            <td class="px-6 py-4">
              <span
                :class="[
                  'inline-block px-2 py-1 rounded text-xs font-semibold',
                  solution.status === 'approve'
                    ? 'bg-green-900 text-green-100'
                    : solution.status === 'reject'
                    ? 'bg-red-900 text-red-100'
                    : 'bg-yellow-900 text-yellow-100',
                ]"
              >
                {{
                  solution.status === "approve"
                    ? "Одобрено"
                    : solution.status === "reject"
                    ? "Отклонено"
                    : "На проверке"
                }}
              </span>
            </td>
            <td class="px-6 py-4 text-sm text-gray-400">
              {{ formatDate(solution.sent_at) }}
            </td>
            <td class="px-6 py-4 text-sm text-gray-400">
              {{
                solution.approved_at ? formatDate(solution.approved_at) : "—"
              }}
            </td>
            <td class="px-6 py-4 text-right space-x-3">
              <button
                v-if="solution.status === 'pending'"
                @click="approveSolution(solution)"
                class="text-green-500 hover:text-green-400"
              >
                Одобрить
              </button>
              <button
                v-if="solution.status === 'pending'"
                @click="rejectSolution(solution)"
                class="text-red-500 hover:text-red-400"
              >
                Отклонить
              </button>
              <button
                v-if="solution.status !== 'pending'"
                @click="removeSolution(solution)"
                class="text-gray-400 hover:text-gray-300"
              >
                Удалить
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Нет решений -->
    <div
      v-else-if="!loading && solutions.length === 0"
      class="text-center text-gray-400"
    >
      Нет решений для этой команды
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import api from "@/services/api";

const solutions = ref([]);
const filter = ref({
  teamId: null,
});
const loading = ref(false);
const errorMessage = ref("");

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString("ru-RU", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
};

// Получить решения
const loadSolutions = async () => {
  if (!filter.value.teamId) {
    errorMessage.value = "Введите ID команды";
    return;
  }

  loading.value = true;
  errorMessage.value = "";

  try {
    const data = await api.admin.getTeamSolutions(filter.value.teamId);
    solutions.value = data.map((solution) => ({
      ...solution,
      status: solution.approved_at
        ? "approve"
        : solution.rejected_at
        ? "reject"
        : "pending",
    }));
  } catch (err) {
    console.error("Ошибка загрузки решений:", err);
    errorMessage.value = "Не удалось загрузить решения";
  } finally {
    loading.value = false;
  }
};

// Одобрить решение
const approveSolution = async (solution) => {
  try {
    await api.admin.approveSolution(
      solution.team_id || filter.value.teamId,
      solution.task_id
    );
    solution.status = "approve";
    solution.approved_at = new Date().toISOString();
  } catch (err) {
    console.error("Ошибка одобрения решения:", err);
    alert("Не удалось одобрить решение");
  }
};

// Отклонить решение
const rejectSolution = async (solution) => {
  try {
    await api.admin.rejectSolution(
      solution.team_id || filter.value.teamId,
      solution.task_id
    );
    solution.status = "reject";
    solution.approved_at = null;
  } catch (err) {
    console.error("Ошибка отклонения решения:", err);
    alert("Не удалось отклонить решение");
  }
};

// Удалить решение
const removeSolution = async (solution) => {
  try {
    await api.admin.removeSolution(
      solution.team_id || filter.value.teamId,
      solution.task_id
    );
    solutions.value = solutions.value.filter(
      (s) => s.solution_id !== solution.solution_id
    );
  } catch (err) {
    console.error("Ошибка удаления решения:", err);
    alert("Не удалось удалить решение");
  }
};
</script>
