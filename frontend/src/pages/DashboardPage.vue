<template>
  <div class="min-h-screen bg-gray-900 text-white">
    <!-- Header -->
    <header
      class="flex justify-between items-center px-6 py-4 bg-gray-800 shadow-md"
    >
      <h1 class="text-2xl font-bold">Дашборд команд</h1>
      <router-link to="/team" class="hover:text-blue-400 transition-colors">
        <!-- Иконка пользователя -->
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
          <circle cx="12" cy="7" r="4"></circle>
        </svg>
      </router-link>
    </header>

    <!-- Loader -->
    <div v-if="loading" class="p-6 text-center text-gray-400">
      Загрузка данных...
    </div>
    <!-- Error Message -->
    <div v-else-if="error" class="p-6 text-center text-red-400">
      {{ error }}
    </div>

    <!-- Таблица -->
    <main v-else class="p-6">
      <div class="overflow-x-auto rounded-lg shadow-lg">
        <table class="w-full table-auto border-collapse">
          <thead>
            <tr
              class="bg-gradient-to-r from-purple-700 to-indigo-800 text-sm uppercase tracking-wider"
            >
              <th class="px-4 py-3 text-left">Команда</th>
              <th class="px-4 py-3 text-center">Статус</th>
              <th v-for="n in maxFiles" :key="n" class="px-2 py-3 text-center">
                {{ n }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(team, index) in teams"
              :key="index"
              class="transition-all duration-300 hover:bg-gray-800 border-b border-gray-700"
            >
              <td class="px-4 py-3 font-medium">{{ team.team_name }}</td>
              <td class="px-4 py-3 text-center">
                <span
                  class="inline-block px-2 py-1 rounded-full text-xs font-semibold"
                  :class="{
                    'bg-red-500 text-white': team.status === 'отключена',
                    'bg-green-500 text-white': team.status === 'подключена',
                    'bg-yellow-500 text-black': ![
                      'отключена',
                      'подключена',
                    ].includes(team.status),
                  }"
                >
                  {{ team.status }}
                </span>
              </td>
              <td
                v-for="fileStatus in getFileStatuses(team.files)"
                :key="fileStatus.index"
                class="px-2 py-3 text-center"
              >
                <span
                  v-if="fileStatus.status"
                  class="block w-23 h-8 mx-auto rounded-full flex items-center justify-center text-xs font-semibold transition-transform transform hover:scale-110"
                  :class="getFileClass(fileStatus.status)"
                >
                  {{ fileStatus.short }}
                </span>
                <span
                  v-else
                  class="block w-23 h-8 mx-auto rounded-full bg-gray-700 text-gray-400 text-xs flex items-center justify-center"
                >
                  —
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      maxFiles: 11,
      teams: [],
      loading: true,
      error: null,
    };
  },
  mounted() {
    this.fetchTeams();
  },
  methods: {
    async fetchTeams() {
      try {
        const token = localStorage.getItem("token");
        const response = await axios.get(
          "http://rocketloud.ru:8000/dashboard/",
          {
            headers: {
              Authorization: `Bearer ${token}`,
              Accept: "application/json",
            },
          }
        );
        // Убедимся, что `teams` это массив
        this.teams = Array.isArray(response.data) ? response.data : [];
      } catch (err) {
        console.error("Ошибка загрузки команд", err);
        this.error = "Не удалось загрузить данные";
      } finally {
        this.loading = false;
      }
    },
    getFileStatuses(files) {
      const result = [];
      for (let i = 1; i <= this.maxFiles; i++) {
        const status = files[i] || "";
        const trimmedStatus = status.trim();
        result.push({
          index: i,
          status: trimmedStatus,
          short: trimmedStatus.toUpperCase(),
        });
      }
      return result;
    },
    getFileClass(status) {
      switch (status) {
        case "зачет":
          return "bg-green-500 text-white";
        case "отправлен":
          return "bg-blue-500 text-white";
        case "не зачёт":
        case "отклонено":
          return "bg-red-400 text-black";
        case "ожидает":
          return "bg-yellow-400 text-black";
        default:
          return "bg-gray-700 text-gray-400";
      }
    },
  },
};
</script>
