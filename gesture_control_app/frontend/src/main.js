import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'

console.log('🚀 Vue应用开始初始化...')

const app = createApp(App)
const pinia = createPinia()

console.log('✅ Pinia创建成功')

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

console.log('✅ Element Plus图标注册完成')

app.use(pinia)
app.use(router)
app.use(ElementPlus)

console.log('✅ 插件注册完成，准备挂载应用...')

app.mount('#app')

console.log('✅ Vue应用挂载成功！')
console.log('📍 当前路由:', router.currentRoute.value.path)

