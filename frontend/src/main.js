import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'

import Login from './views/Login.vue'
import Register from './views/Register.vue'
import ForgotPassword from './views/ForgotPassword.vue'
import Dashboard from './views/Dashboard.vue'
import Projects from './views/Projects.vue'
import ProjectNew from './views/ProjectNew.vue'
import ProjectDetail from './views/ProjectDetail.vue'
import ProjectSettings from './views/ProjectSettings.vue'
import Tasks from './views/Tasks.vue'
import TaskDetail from './views/TaskDetail.vue'
import TaskNew from './views/TaskNew.vue'
import TaskEdit from './views/TaskEdit.vue'
import Team from './views/Team.vue'
import Settings from './views/Settings.vue'
import SettingsBilling from './views/SettingsBilling.vue'
import Export from './views/Export.vue'

const routes = [
  { path: '/login', component: Login, meta: { public: true } },
  { path: '/register', component: Register, meta: { public: true } },
  { path: '/forgot-password', component: ForgotPassword, meta: { public: true } },
  { path: '/dashboard', component: Dashboard },
  { path: '/projects', component: Projects },
  { path: '/projects/new', component: ProjectNew },
  { path: '/projects/:id', component: ProjectDetail, props: true },
  { path: '/projects/:id/settings', component: ProjectSettings, props: true },
  { path: '/projects/:id/tasks', component: Tasks, props: true },
  { path: '/projects/:id/tasks/new', component: TaskNew, props: true },
  { path: '/projects/:id/tasks/:taskId', component: TaskDetail, props: true },
  { path: '/projects/:id/tasks/:taskId/edit', component: TaskEdit, props: true },
  { path: '/projects/:id/team', component: Team, props: true },
  { path: '/projects/:id/export', component: Export, props: true },
  { path: '/settings/profile', component: Settings },
  { path: '/settings/billing', component: SettingsBilling },
  { path: '/settings/notifications', component: Settings },
  { path: '/', redirect: '/dashboard' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Auth guard
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('teamflow_token')
  if (!to.meta.public && !token) {
    next('/login')
  } else {
    next()
  }
})

const app = createApp(App)
app.use(router)
app.mount('#app')
