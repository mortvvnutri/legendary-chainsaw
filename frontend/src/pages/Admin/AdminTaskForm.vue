<template>
  <div class="max-w-2xl mx-auto">
    <h2 class="text-2xl font-bold mb-6">
      {{ isEdit ? "Редактировать задачу" : "Новая задача" }}
    </h2>

    <div class="bg-gray-800 rounded-lg shadow-lg p-6">
      <form @submit.prevent="submitTask">
        <div class="mb-4">
          <label class="block text-sm font-medium mb-2">Вопрос</label>
          <textarea
            v-model="task.question"
            rows="4"
            class="w-full bg-gray-700 border border-gray-600 rounded p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          ></textarea>
        </div>

        <div class="mb-4">
          <label class="block text-sm font-medium mb-2">Правильный ответ</label>
          <div class="bg-gray-700 p-4 rounded">
            <div class="grid grid-cols-1 gap-4">
              <input
                v-model="task.answer.selections[0].type"
                placeholder="Тип ошибки"
                class="bg-gray-800 p-2 border border-gray-600 rounded"
                required
              />
              <div class="flex space-x-4">
                <input
                  v-model.number="task.answer.selections[0].startSelection"
                  type="number"
                  placeholder="Start"
                  class="bg-gray-800 p-2 border border-gray-600 rounded w-1/2"
                  required
                />
                <input
                  v-model.number="task.answer.selections[0].endSelection"
                  type="number"
                  placeholder="End"
                  class="bg-gray-800 p-2 border border-gray-600 rounded w-1/2"
                  required
                />
              </div>
            </div>
          </div>
        </div>

        <div class="flex space-x-4 mt-6">
          <button
            type="submit"
            class="bg-green-600 hover:bg-green-700 px-4 py-2 rounded flex-1"
          >
            {{ isEdit ? "Сохранить" : "Добавить" }} задачу
          </button>

          <button
            v-if="isEdit"
            @click="clearForm"
            type="button"
            class="bg-gray-600 hover:bg-gray-700 px-4 py-2 rounded"
          >
            Отменить
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "@/services/api";

const tasks = ref([]);
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString();
};

const isEdit = ref(false);

async function submitTask() {
  try {
    await api.admin.createTask(task.value);
    alert("Задача успешно добавлена!");
    task.value = {
      question: "",
      answer: {
        selections: [
          {
            type: "",
            startSelection: null,
            endSelection: null,
          },
        ],
      },
    };
  } catch (err) {
    console.error("Ошибка отправки задачи", err);
    alert("Не удалось добавить задачу");
  }
}
</script>
