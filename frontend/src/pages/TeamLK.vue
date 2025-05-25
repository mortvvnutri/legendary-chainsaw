<template>
  <div class="min-h-screen bg-gray-900 text-white p-6">
    <h1 class="text-3xl font-bold mb-6">Личный кабинет команды</h1>

    <!-- Статус -->
    <div v-if="loading" class="text-center text-gray-400">
      Загрузка данных...
    </div>
    <div v-if="!tasks.length && error" class="text-red-400 text-center">
      {{ error }}
    </div>

    <!-- Список задач -->
    <div v-if="tasks.length">
      <div
        v-for="task in tasks"
        :key="task.task_id"
        class="bg-gray-800 rounded-lg shadow-lg p-6 mb-6"
      >
        <!-- Заголовок задачи -->
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-semibold">Задание №{{ task.task_id }}</h2>
          <span
            class="px-3 py-1 text-sm rounded-full font-medium"
            :class="{
              'bg-green-600 text-white': task.status === 'approve',
              'bg-red-600 text-white': task.status === 'reject',
              'bg-blue-600 text-white': task.status === '',
              'bg-yellow-600 text-white': task.status === 'pending',
            }"
          >
            {{
              task.status === "approve"
                ? "Одобрено"
                : task.status === "reject"
                ? "Отклонено"
                : task.status === "pending"
                ? "На проверке"
                : "Активно"
            }}
          </span>
        </div>

        <!-- Вопрос -->
        <p class="mb-6 text-lg">{{ task.question }}</p>

        <!-- Форма решения -->
        <div class="mt-6 space-y-4">
          <!-- Форма активна только если статус пустой -->
          <div v-if="task.status === ''">
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
              :disabled="task.loading"
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

          <!-- Статусы -->
          <div v-else-if="task.status === 'approve'" class="mt-6 text-center">
            <p class="text-lg font-semibold text-green-400">✅ Ответ одобрен</p>
          </div>
          <div v-else-if="task.status === 'reject'" class="mt-6 text-center">
            <p class="text-lg font-semibold text-red-400">❌ Ответ отклонён</p>
          </div>
          <div v-else class="mt-6 text-center">
            <p class="text-lg font-semibold text-yellow-400">
              🕒 Отправлено на проверку
            </p>
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
import { ref, onMounted, onUnmounted } from "vue";
import axios from "axios";

export default {
  setup() {
    const token = localStorage.getItem("token");
    const tasks = ref([]);
    const loading = ref(true);
    const error = ref(null);
    const ws = ref(null);
    let pingInterval = null;
    let fetchInterval = null;

    // Подключение WebSocket
    const connectWebSocket = () => {
      if (!token) return;

      ws.value = new WebSocket(
        `ws://rocketloud.ru:8000/ws/team/status?token=${token}`
      );

      ws.value.onopen = () => {
        pingInterval = setInterval(() => {
          if (ws.value?.readyState === WebSocket.OPEN) {
            ws.value.send("ping");
          }
        }, 5000);
      };

      ws.value.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.tasks && Array.isArray(data.tasks)) {
            data.tasks.forEach((updatedTask) => {
              const task = tasks.value.find(
                (t) => t.task_id === updatedTask.task_id
              );
              if (task) {
                task.status = updatedTask.status;
              }
            });
          }
        } catch (e) {
          console.error("Ошибка парсинга WebSocket-ответа", e);
        }
      };

      ws.value.onclose = () => {
        clearInterval(pingInterval);
        ws.value = null;
      };

      ws.value.onerror = (err) => {
        console.error("WebSocket Error:", err);
        clearInterval(pingInterval);
        ws.value = null;
      };
    };

    // Очистка при размонтировании
    onUnmounted(() => {
      if (ws.value) {
        ws.value.close();
        ws.value = null;
      }
      if (pingInterval) clearInterval(pingInterval);
      if (fetchInterval) clearInterval(fetchInterval);
    });
    // Получение задач
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

        if (!Array.isArray(res.data.tasks)) {
          throw new Error("Неверный формат задач");
        }

        tasks.value = res.data.tasks.map((task) => ({
          ...task,
          task_id: Number(task.task_id),
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
        typeof task.formData.endSelection === "number"
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
        debugger;
        const payload = {
          task_id: task.task_id,
          answer: {
            selections: [
              {
                type: task.formData.type,
                startSelection: task.formData.startSelection,
                endSelection: task.formData.endSelection,
              },
            ],
          },
        };

        const res = await axios.post(
          "http://rocketloud.ru:8000/team/tasks/answer_load",
          payload,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("token")}`,
              "Content-Type": "application/json",
            },
          }
        );

        console.log("Ответ от сервера:", res.data);

        task.successMessage = "Решение отправлено!";
        task.status = "pending";
        task.formData = {
          type: "",
          startSelection: null,
          endSelection: null,
        };
      } catch (err) {
        const status = err.response?.status;
        const data = err.response?.data || {};

        console.error("Ошибка отправки решения:", {
          status,
          data,
          message: err.message,
        });

        switch (status) {
          case 400:
            task.errorMessage =
              data.detail || "Неверные данные или задача не найдена";
            break;
          case 401:
            task.errorMessage = "Неавторизован";
            break;
          case 409:
            task.errorMessage = "Решение уже отправлено";
            task.status = "reject";
            break;
          case 500:
            task.errorMessage = "Внутренняя ошибка сервера";
            break;
          case 503:
            task.errorMessage = "Сервер недоступен";
            break;
          default:
            task.errorMessage = data.detail || "Не удалось отправить решение";
        }
      } finally {
        task.loading = false;
      }
    };

    // Загрузка задач
    onMounted(() => {
      connectWebSocket();
      fetchTasks();
      fetchInterval = setInterval(fetchTasks, 45_000);
    });

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
