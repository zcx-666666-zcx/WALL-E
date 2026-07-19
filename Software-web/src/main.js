import { createApp } from 'vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'

import './assets/main.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import { loadPublicConfig } from './utils/systemConfig'
import { bootstrapApp } from './bootstrap.mjs'

const app = createApp(App)
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(router)
app.use(ElementPlus)

bootstrapApp(loadPublicConfig, () => app.mount('#app'))
