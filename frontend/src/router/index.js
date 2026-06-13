import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/LoginView.vue'),
  },
  {
    path: '/',
    name: 'dashboard',
    component: () => import('../views/DashboardView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/qc',
    name: 'qc-monitor',
    component: () => import('../views/QCMonitorView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/sigma',
    name: 'sigma',
    component: () => import('../views/SigmaView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/validation',
    name: 'validation',
    component: () => import('../views/ValidatorView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/audit',
    name: 'audit',
    component: () => import('../views/AuditView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/eqa',
    name: 'eqa',
    component: () => import('../views/EQAView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/lots',
    name: 'lot-registry',
    component: () => import('../views/LotRegistryView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/regulatory',
    name: 'regulatory-assistant',
    component: () => import('../views/RegulatoryAssistantView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/learn',
    name: 'learn',
    component: () => import('../views/LearnView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('../views/SettingsView.vue'),
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory('/labqc/'),
  routes,
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('labqc_token')
  if (to.name === 'login') {
    // Already logged in → redirect to home
    if (token) return next('/')
    return next()
  }
  if (to.meta.requiresAuth && !token) {
    return next({ name: 'login', query: { redirect: to.fullPath } })
  }
  next()
})

export default router
