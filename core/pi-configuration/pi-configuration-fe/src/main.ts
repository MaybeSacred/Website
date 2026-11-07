import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue-next/dist/bootstrap-vue-next.css'
import './assets/main.css'

import { createApp } from 'vue'
import { createBootstrap } from 'bootstrap-vue-next/plugins/createBootstrap'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(router)
app.use(createBootstrap())

app.mount('#app')
