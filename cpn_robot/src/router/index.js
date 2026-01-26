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
import VideoView from '@/views/video/video.vue';
import DriveView from '@/views/drive/web_interface/templates/index.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: '',
      component: LayoutView,
      redirect: '/index',
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
        {path: 'video', name: 'video', component: VideoView},
        {path: 'drive', name: 'drive', component: DriveView}
      ]
    },
    {path: '/login', name: 'login', component: loginView}
  ]
})

export default router
