import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // если у вас есть роутер
import './assets/styles/main.css'
const app = createApp(App)

app.use(router) // если используется

app.mount('#app')