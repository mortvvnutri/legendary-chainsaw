<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-900 px-4">
    <div class="max-w-md w-full bg-gray-800 p-8 rounded-xl shadow-lg">
      <h2 class="text-2xl font-bold text-white text-center mb-6">
        Авторизация
      </h2>

      <form @submit.prevent="handleSubmit" class="space-y-5">
        <!-- Логин -->
        <div>
          <label
            for="login"
            class="block text-sm font-medium text-gray-300 mb-1"
            >Логин</label
          >
          <input
            type="text"
            id="login"
            v-model="form.login"
            required
            placeholder="Введите ваш логин"
            class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <!-- Пароль -->
        <div>
          <label
            for="password"
            class="block text-sm font-medium text-gray-300 mb-1"
            >Пароль</label
          >
          <input
            type="password"
            id="password"
            v-model="form.password"
            required
            placeholder="Введите пароль"
            class="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <!-- Сообщение об ошибке -->
        <div v-if="errorMessage" class="text-red-400 text-sm text-center">
          {{ errorMessage }}
        </div>

        <!-- Кнопка входа -->
        <button
          type="submit"
          :disabled="isLoading"
          class="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold rounded-md transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          {{ isLoading ? "Вход..." : "Войти" }}
        </button>
      </form>
    </div>
  </div>
</template>

<script>
import { ref } from "vue";
import { useRouter } from "vue-router";
import auth from "../services/api/auth";

export default {
  setup() {
    const router = useRouter();
    const form = ref({
      login: "",
      password: "",
    });
    const errorMessage = ref("");
    const isLoading = ref(false);

    const handleSubmit = async () => {
      errorMessage.value = "";
      isLoading.value = true;

      try {
        const res = await auth.login({
          login: form.value.login,
          password: form.value.password,
        });

        localStorage.setItem("token", res.token);
        const redirect = router.currentRoute.value.query.redirect || "/team";
        router.push(redirect);
      } catch (error) {
        errorMessage.value = "Неверный логин или пароль";
        console.error("Ошибка авторизации:", error);
      } finally {
        isLoading.value = false;
      }
    };

    return {
      form,
      errorMessage,
      isLoading,
      handleSubmit,
    };
  },
};
</script>
