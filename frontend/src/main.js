import { createApp } from 'vue'
import App from './App.vue'

import './assets/styles.css'
import './../node_modules/@fortawesome/fontawesome-free/css/all.min.css'
import router from './router'

const app = createApp(App)

app.config.errorHandler = (err) => {
    console.log("Error:", err);
};

app.use(router)

app.mount('#app')
