<script setup>
import { useRoute } from 'vue-router'
import { ref, computed, provide } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  LayoutDashboard,
  Activity,
  TrendingUp,
  ClipboardCheck,
  Shield,
  Package,
  BookOpen,
  GraduationCap,
  Settings,
  PanelLeftClose,
  PanelLeftOpen,
} from 'lucide-vue-next'

const { t } = useI18n()
const route = useRoute()

const sidebarCollapsed = ref(false)
provide('sidebarCollapsed', sidebarCollapsed)

const navItems = [
  { to: '/', key: 'nav.dashboard', icon: LayoutDashboard },
  { to: '/qc', key: 'nav.qcMonitor', icon: Activity },
  { to: '/sigma', key: 'nav.sigmaAnalysis', icon: TrendingUp },
  { to: '/validation', key: 'nav.validation', icon: ClipboardCheck },
  { to: '/audit', key: 'nav.auditTrail', icon: Shield },
  { to: '/lots', key: 'nav.lotRegistry', icon: Package },
  { to: '/regulatory', key: 'nav.regulatory', icon: BookOpen },
  { to: '/learn', key: 'nav.learn', icon: GraduationCap },
]

const bottomNavItems = [
  { to: '/settings', key: 'nav.settings', icon: Settings },
]

function isActive(item) {
  if (item.to === '/') return route.path === '/'
  return route.path.startsWith(item.to)
}

function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
}
</script>

<template>
  <div class="app-shell">
    <aside class="sidebar" :class="{ 'sidebar--collapsed': sidebarCollapsed }">
      <div class="sidebar-header">
        <img v-if="!sidebarCollapsed" src="@/assets/ksc-logo.svg" alt="LabQC" class="logo-img" />
        <span v-else class="logo-icon">LQ</span>
        <button class="sidebar-toggle" @click="toggleSidebar" :title="sidebarCollapsed ? t('nav.expandSidebar') : t('nav.collapseSidebar')">
          <PanelLeftOpen v-if="sidebarCollapsed" :size="18" :stroke-width="1.75" />
          <PanelLeftClose v-else :size="18" :stroke-width="1.75" />
        </button>
      </div>
      <nav class="sidebar-nav">
        <router-link
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="nav-link"
          :class="{ 'nav-link--active': isActive(item) }"
          :title="sidebarCollapsed ? t(item.key) : undefined"
        >
          <component :is="item.icon" :size="18" :stroke-width="1.75" />
          <span v-if="!sidebarCollapsed">{{ t(item.key) }}</span>
        </router-link>
      </nav>
      <div class="sidebar-bottom">
        <nav class="sidebar-nav">
          <router-link
            v-for="item in bottomNavItems"
            :key="item.to"
            :to="item.to"
            class="nav-link"
            :class="{ 'nav-link--active': isActive(item) }"
            :title="sidebarCollapsed ? t(item.key) : undefined"
          >
            <component :is="item.icon" :size="18" :stroke-width="1.75" />
            <span v-if="!sidebarCollapsed">{{ t(item.key) }}</span>
          </router-link>
        </nav>
      </div>
    </aside>
    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.app-shell {
  display: flex;
  min-height: 100vh;
  min-height: 100dvh;
}

.sidebar {
  width: 240px;
  flex-shrink: 0;
  background-color: var(--bg-surface);
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--border-subtle);
  transition: width 0.2s ease;
}

.sidebar--collapsed {
  width: 56px;
}

.sidebar-header {
  padding: 16px 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  min-height: 56px;
}

.sidebar--collapsed .sidebar-header {
  justify-content: center;
  padding: 16px 8px;
}

.logo-img {
  height: 28px;
  width: auto;
  object-fit: contain;
}

.logo-icon {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 0.05em;
}

.sidebar-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: 6px;
  flex-shrink: 0;
  transition: color 0.15s, background-color 0.15s;
}

.sidebar-toggle:hover {
  color: var(--text-secondary);
  background-color: var(--bg-surface-2);
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 0 8px;
}

.sidebar--collapsed .sidebar-nav {
  padding: 0 6px;
}

.sidebar-bottom {
  margin-top: auto;
  padding-top: 8px;
  padding-bottom: 12px;
  border-top: 1px solid var(--border-subtle);
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  border-radius: 6px;
  color: var(--text-muted);
  text-decoration: none;
  font-size: 18px;
  font-weight: 450;
  transition: color 0.15s ease, background-color 0.15s ease;
  white-space: nowrap;
  overflow: hidden;
}

.sidebar--collapsed .nav-link {
  justify-content: center;
  padding: 9px;
  gap: 0;
}

.nav-link:hover {
  color: var(--text-secondary);
  background-color: var(--bg-surface-2);
}

.nav-link--active {
  color: var(--text-primary);
  background-color: var(--bg-highlight);
}

.content {
  flex: 1;
  min-width: 0;
  background-color: var(--bg-app);
  overflow-y: auto;
}
</style>
