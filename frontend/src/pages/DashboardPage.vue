<template>
  <div class="min-h-screen bg-gray-900 text-white p-6">
    <h1 class="text-3xl font-bold mb-6">Дашборд команд</h1>

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
                  'bg-yellow-500 text-black':
                    team.status !== 'отключена' && team.status !== 'подключена',
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
                class="block w-8 h-8 mx-auto rounded-full flex items-center justify-center text-xs font-semibold transition-transform transform hover:scale-110"
                :class="getFileClass(fileStatus.status)"
              >
                {{ fileStatus.short }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      maxFiles: 7,
      teams: [
        {
          team_name: "admin",
          status: "отключена",
          files: {},
        },
        {
          team_name: "luba",
          status: "отключена",
          files: {},
        },
        {
          team_name: "команда_3",
          status: "подключена",
          files: {
            1: "зачет",
            2: "зачет",
            3: "отправлен",
            4: "зачет",
            5: "ожидает",
            6: "зачет",
          },
        },
        {
          team_name: "новая_команда",
          status: "ожидает",
          files: {
            1: "ожидает",
            2: "отправлен",
          },
        },
      ],
    };
  },
  methods: {
    getFileStatuses(files) {
      const result = [];
      for (let i = 1; i <= this.maxFiles; i++) {
        let status = files[i] || "";
        result.push({
          index: i,
          status,
          short: status.slice(0, 1).toUpperCase(),
        });
      }
      return result;
    },
    getFileClass(status) {
      if (status === "зачет") {
        return "bg-green-500 text-white";
      } else if (status === "отправлен") {
        return "bg-blue-500 text-white";
      } else if (status === "ожидает") {
        return "bg-yellow-400 text-black";
      } else {
        return "bg-gray-700 text-gray-400";
      }
    },
  },
};
</script>

<style scoped>
/* Встроенные стили не нужны, всё через Tailwind */
</style>
