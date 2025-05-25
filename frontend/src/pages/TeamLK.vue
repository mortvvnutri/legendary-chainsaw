<template>
  <div class="min-h-screen bg-gray-900 text-white p-6">
    <h1 class="text-3xl font-bold mb-6">
      Личный кабинет команды #{{ teamId }}
    </h1>

    <!-- Задание -->
    <div v-if="task" class="bg-gray-800 rounded-lg shadow-lg p-6 mb-6">
      <h2 class="text-xl font-semibold mb-4">Задание</h2>
      <p class="mb-2"><strong>Описание:</strong> {{ task.description }}</p>
      <pre class="bg-gray-700 p-4 rounded overflow-x-auto">{{ task.code }}</pre>

      <div class="mt-6 space-y-4">
        <h3 class="font-medium mb-2">Укажите решение</h3>

        <!-- Тип ошибки -->
        <div>
          <label for="type" class="block text-sm font-medium mb-1"
            >Тип ошибки</label
          >
          <select
            v-model="formData.type"
            id="type"
            class="w-full p-2 bg-gray-700 rounded text-white"
          >
            <option disabled value="">Выберите тип ошибки</option>
            <option value="ЛОГИЧЕСКАЯ ОШИБКА">Логическая ошибка</option>
            <option value="СИНТАКСИЧЕСКАЯ ОШИБКА">Синтаксическая ошибка</option>
            <option value="ПРОИЗВОДИТЕЛЬНОСТЬ">
              Проблема производительности
            </option>
            <option value="БЕЗОПАСНОСТЬ">Потенциальная уязвимость</option>
            <option value="СТИЛЬ">Нарушение стиля кодирования</option>
          </select>
        </div>

        <!-- Start Selection -->
        <div>
          <label for="startSelection" class="block text-sm font-medium mb-1"
            >Start Selection</label
          >
          <input
            type="number"
            v-model.number="formData.startSelection"
            id="startSelection"
            placeholder="Введите начальную позицию"
            class="w-full p-2 bg-gray-700 rounded text-white"
          />
        </div>

        <!-- End Selection -->
        <div>
          <label for="endSelection" class="block text-sm font-medium mb-1"
            >End Selection</label
          >
          <input
            type="number"
            v-model.number="formData.endSelection"
            id="endSelection"
            placeholder="Введите конечную позицию"
            class="w-full p-2 bg-gray-700 rounded text-white"
          />
        </div>

        <!-- Кнопка отправки -->
        <button
          @click="submitSelection"
          :disabled="loading || !isFormValid"
          class="mt-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded disabled:bg-blue-400 w-full"
        >
          {{ loading ? "Отправка..." : "Отправить решение" }}
        </button>

        <!-- Сообщения -->
        <div v-if="errorMessage" class="text-red-400 text-sm mt-2">
          {{ errorMessage }}
        </div>
        <div v-if="successMessage" class="text-green-400 text-sm mt-2">
          {{ successMessage }}
        </div>
      </div>
    </div>

    <div v-else class="text-center text-gray-400">Нет доступных заданий</div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import axios from "axios";

export default {
  setup() {
    const route = useRoute();
    const router = useRouter();

    const teamId = ref(route.params.id);
    const task = ref(null);
    const codeSnippet = ref("");
    const loading = ref(false);

    // Получение задания
    const fetchTask = async () => {
      try {
        const res = await axios.get(
          `http://rocketloud.ru:8000/team/tasks/get_task`,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("token")}`,
              Accept: "application/json",
            },
          }
        );
        task.value = {
          description: res.data.description,
          code: res.data.code,
        };
      } catch (err) {
        console.error("Ошибка получения задания", err);
      }
    };

    // Отправка выделенного участка
    const submitSelection = async () => {
      if (!codeSnippet.value.trim()) return;

      loading.value = true;

      // Пример: вычисляем старт и конец выделения
      const startSelection = 5;
      const endSelection = startSelection + codeSnippet.value.length;

      try {
        await axios.post(
          `http://rocketloud.ru:8000/solutions/`,
          {
            selections: [
              {
                type: "ЛОГИЧЕСКАЯ ОШИБКА",
                startSelection,
                endSelection,
              },
            ],
          },
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("token")}`,
              "Content-Type": "application/json",
            },
          }
        );

        alert("Решение отправлено!");
      } catch (err) {
        console.error("Ошибка отправки решения", err);
        alert("Не удалось отправить решение");
      } finally {
        loading.value = false;
      }
    };

    onMounted(() => {
      fetchTask();
    });

    return {
      teamId,
      task,
      codeSnippet,
      loading,
      submitSelection,
    };
  },
};
</script>
