<template>
  <div class="login-form">
    <h2>Авторизация</h2>
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="email">Email:</label>
        <input
          type="email"
          id="email"
          v-model="form.email"
          required
          placeholder="Введите ваш email"
        />
      </div>
      
      <div class="form-group">
        <label for="password">Пароль:</label>
        <input
          type="password"
          id="password"
          v-model="form.password"
          required
          placeholder="Введите пароль"
        />
      </div>
      
      <button type="submit" :disabled="isLoading">
        {{ isLoading ? 'Вход...' : 'Войти' }}
      </button>
      
      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>
    </form>
  </div>
</template>

<script>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

export default {
  setup() {
    const router = useRouter();
    const form = ref({
      email: '',
      password: ''
    });
    const errorMessage = ref('');
    const isLoading = ref(false);

    const handleSubmit = async () => {
      errorMessage.value = '';
      isLoading.value = true;
      
      try {
        // Здесь должна быть логика авторизации, например, запрос к API
        // const response = await authService.login(form.value);
        
        // Имитация запроса
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // В реальном приложении здесь бы проверялся ответ от сервера
        // и сохранялся токен авторизации
        localStorage.setItem('isAuthenticated', 'true');
        
        // Перенаправление на защищенную страницу
        router.push('/dashboard');
      } catch (error) {
        errorMessage.value = 'Неверный email или пароль';
        console.error('Ошибка авторизации:', error);
      } finally {
        isLoading.value = false;
      }
    };

    return {
      form,
      errorMessage,
      isLoading,
      handleSubmit
    };
  }
};
</script>

<style scoped>
.login-form {
  max-width: 400px;
  margin: 0 auto;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}

button {
  width: 100%;
  padding: 10px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.error-message {
  margin-top: 10px;
  color: #ff4444;
  font-size: 14px;
}
</style>
