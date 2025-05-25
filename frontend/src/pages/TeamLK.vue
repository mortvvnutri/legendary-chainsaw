<template>
  <div class="min-h-screen bg-gray-900 text-white p-6">
    <h1 class="text-3xl font-bold mb-6">Личный кабинет команды</h1>

    <!-- Статус -->
    <div v-if="loading" class="text-center text-gray-400">
      Загрузка данных...
    </div>
    <div v-else-if="error" class="text-red-400 text-center">{{ error }}</div>

    <!-- Список задач -->
    <div v-else>
      <div
        v-for="task in tasks"
        :key="task.task_id"
        class="bg-gray-800 rounded-lg shadow-lg p-6 mb-6"
      >
        <!-- Заголовок задачи -->
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-semibold">
            Задание №{{ task.task_id || "—" }}
          </h2>
          <span class="px-3 py-1 bg-blue-600 rounded-full text-sm"
            >Активно</span
          >
        </div>

        <!-- Вопрос -->
        <p class="mb-6 text-lg">
          {{ task.question || "Вопрос не загружен..." }}
        </p>

        <!-- Форма решения -->
        <div class="mt-6 space-y-4">
          <h3 class="font-medium mb-2">Укажите решение</h3>

          <!-- Тип ошибки -->
          <div>
            <label for="type" class="block text-sm font-medium mb-1"
              >Тип ошибки</label
            >
            <select
              v-model="task.formData.type"
              id="type"
              class="w-full p-2 bg-gray-700 rounded text-white"
            >
              <option disabled value="">Выберите тип ошибки</option>
              <option value="ЛОГИЧЕСКАЯ ОШИБКА">Логическая ошибка</option>
              <option value="СИНТАКСИЧЕСКАЯ ОШИБКА">
                Синтаксическая ошибка
              </option>
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
              v-model.number="task.formData.startSelection"
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
              v-model.number="task.formData.endSelection"
              id="endSelection"
              placeholder="Введите конечную позицию"
              class="w-full p-2 bg-gray-700 rounded text-white"
            />
          </div>

          <!-- Кнопка отправки -->
          <button
            @click="submitSelection(task)"
            :disabled="task.loading || !isFormValid(task)"
            class="mt-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded disabled:bg-blue-400 w-full"
          >
            {{ task.loading ? "Отправка..." : "Отправить решение" }}
          </button>

          <!-- Сообщения -->
          <div v-if="task.errorMessage" class="text-red-400 text-sm mt-2">
            {{ task.errorMessage }}
          </div>
          <div v-if="task.successMessage" class="text-green-400 text-sm mt-2">
            {{ task.successMessage }}
          </div>
        </div>
      </div>

      <!-- Нет задач -->
      <div
        v-if="tasks.length === 0 && !loading && !error"
        class="text-center text-gray-400"
      >
        Нет доступных заданий
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";

export default {
  setup() {
    const token = localStorage.getItem("token");
    const tasks = ref([]);
    const loading = ref(true);
    const error = ref(null);

    // Подключение WebSocket (не используется пока)
    const ws = new WebSocket(
      `ws://rocketloud.ru:8000/ws/team/status?token=${token}`
    );
    ws.onopen = () => {
      setInterval(() => ws.send("ping"), 5000);
    };

    // Загрузка задач
    const fetchTasks = async () => {
      try {
        const res = await axios.get(
          "http://rocketloud.ru:8000/team/tasks/get_task",
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("token")}`,
              Accept: "application/json",
            },
          }
        );

        // Инициализируем каждую задачу с собственной формой
        tasks.value = res.data.tasks.map((task) => ({
          ...task,
          formData: {
            type: "",
            startSelection: null,
            endSelection: null,
          },
          loading: false,
          errorMessage: "",
          successMessage: "",
        }));
      } catch (err) {
        console.error("Ошибка получения задания", err);
        error.value = "Не удалось загрузить задания";
      } finally {
        loading.value = false;
      }
    };

    // Валидация формы
    const isFormValid = (task) => {
      return (
        task.formData.type &&
        typeof task.formData.startSelection === "number" &&
        typeof task.formData.endSelection === "number" &&
        task.formData.endSelection > task.formData.startSelection
      );
    };

    // Отправка решения
    const submitSelection = async (task) => {
      if (!isFormValid(task)) {
        task.errorMessage = "Заполните все поля корректно.";
        task.successMessage = "";
        return;
      }

      task.loading = true;
      task.errorMessage = "";
      task.successMessage = "";

      try {
        await axios.post(
          "http://rocketloud.ru:8000/solutions/",
          {
            selections: [
              {
                type: task.formData.type,
                startSelection: task.formData.startSelection,
                endSelection: task.formData.endSelection,
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

        task.successMessage = "Решение успешно отправлено!";
        task.formData = {
          type: "",
          startSelection: null,
          endSelection: null,
        };
      } catch (err) {
        console.error("Ошибка отправки решения", err);
        task.errorMessage = "Не удалось отправить решение";
      } finally {
        task.loading = false;
      }
    };

    // Загружаем задачи при монтировании
    fetchTasks();

    return {
      tasks,
      loading,
      error,
      submitSelection,
      isFormValid,
    };
  },
};
</script>
