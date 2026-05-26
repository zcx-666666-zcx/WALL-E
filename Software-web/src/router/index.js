import { createRouter, createWebHistory } from 'vue-router';

import loginView from '@/views/login/login.vue';
import ElementlistView from '@/views/elementlist/elementlist.vue';
import AgentView from '@/views/Agent/Agent.vue';
import userView from '@/views/user/user.vue';
import commandView from '@/views/command/command.vue';
import connectionsView from '@/views/connections/connections.vue';
import LayoutView from '@/views/layout/index.vue';
import IndexView from '@/views/index/index.vue';
import InfoView from '@/views/info/info.vue';
import SetView from '@/views/set/set.vue'
import MachineView from '@/views/machines/machines.vue'
import WebrtcVideoView from '@/views/video/webrtc_video.vue'; 
import HealthyView from '@/views/healthy/healthy.vue';
import regisView from '@/views/regis/regis.vue';
import DriveView from '@/views/drive/drive.vue';
import AIView from '@/views/new_agent/Agent_new.vue';
import AdminView from '@/views/admin/admin.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: '',
      component: LayoutView,
      redirect: '/login',
      children: [
        {path: 'elementlist', name: 'elementlist', component: ElementlistView},
        {path: 'Agent', name: 'Agent', component: AgentView},
        {path: 'user', name: 'user', component: userView},
        {path: 'command', name: 'command', component: commandView},
        {path: 'connections', name: 'connections', component: connectionsView},
        {path: 'index', name: 'index', component: IndexView},
        {path: 'info', name: 'info', component: InfoView},
        {path: 'set', name: 'set', component: SetView},
        {path: 'machines', name: 'machines', component: MachineView},
        {path: 'video', name: 'video', redirect: '/webrtc-video'}, // 重定向到新视频通话页面
        {path: 'webrtc-video', name: 'webrtc-video', component: WebrtcVideoView}, // 新增路由
        {path: 'drive', name: 'drive' ,component: DriveView},
        {path: 'healthy', name: 'healthy', component: HealthyView},
        {path: 'new_agent', name: 'new_agent' ,component: AIView},
        {path: 'admin', name: 'admin', component: AdminView}
      ]
    },
    {path: '/login', name: 'login', component: loginView},
    {path: '/regis', name: 'regis', component: regisView}
  ]
})

const getToken = () => {
  const user = localStorage.getItem('loginUserObject')
  if (!user) return null
  try {
    const obj = JSON.parse(user)
    return obj.token || null
  } catch {
    return null
  }
}

const getLoginUser = () => {
  const user = localStorage.getItem('loginUserObject')
  if (!user) return null
  try {
    return JSON.parse(user)
  } catch {
    return null
  }
}

router.beforeEach((to, from, next) => {
  const token = getToken()

  if (to.path === '/login' || to.path === '/regis') {
    // 已登录用户访问登录页，直接跳到首页
    if (token) return next('/index')
    return next()
  }

  // 访问受保护页面但没有 token，跳转到登录页
  if (!token) return next('/login')

  if (to.path === '/admin' && getLoginUser()?.role !== 'admin') {
    return next('/index')
  }

  next()
})

export default router
