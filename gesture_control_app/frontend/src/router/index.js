import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import PPTControl from '../views/PPTControl.vue'
import VideoControl from '../views/VideoControl.vue'
import Settings from '../views/Settings.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/ppt',
    name: 'PPTControl',
    component: PPTControl
  },
  {
    path: '/video',
    name: 'VideoControl',
    component: VideoControl
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router

