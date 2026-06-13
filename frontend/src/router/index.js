import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/activate',
    name: 'activate',
    component: () => import('../views/ActivateView.vue'),
  },
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

let _licenseChecked = false
let _licenseValid = false

router.beforeEach(async (to, _from, next) => {
  // ── License check (once per pageload) ──
  if (!_licenseChecked) {
    _licenseChecked = true
    try {
      const BASE = import.meta.env.BASE_URL
      const r = await fetch(`${BASE}license/status`)
      const d = await r.json()
      _licenseValid = d.valid
    } catch {
      _licenseValid = false
    }
  }

  // If unlicensed, redirect to activate (allow activate page itself)
  if (!_licenseValid && to.name !== 'activate') {
    return next('/activate')
  }

  // If licensed and on activate page, go to login
  if (_licenseValid && to.name === 'activate') {
    return next('/login')
  }

  const token = localStorage.getItem('labqc_token')
  if (to.name === 'login') {
    if (token) return next('/')
    return next()
  }
  if (to.meta.requiresAuth && !token) {
    return next({ name: 'login', query: { redirect: to.fullPath } })
  }
  next()
})

export default router
