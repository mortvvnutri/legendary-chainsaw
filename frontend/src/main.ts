import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // если у вас есть роутер

const app = createApp(App)

app.use(router) // если используется

app.mount('#app')