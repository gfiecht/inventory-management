<template>
  <!-- Mobile backdrop -->
  <div
    v-if="mobileOpen"
    class="sidebar-backdrop"
    @click="closeMobile"
  ></div>

  <aside
    class="sidebar"
    :class="{
      'sidebar--collapsed': effectiveCollapsed,
      'sidebar--mobile-open': mobileOpen
    }"
  >
    <!-- Logo -->
    <div class="sidebar-logo">
      <div class="logo-mark">C</div>
      <div v-if="!effectiveCollapsed" class="logo-text">
        <span class="logo-company">{{ t('nav.companyName') }}</span>
        <span class="logo-subtitle">{{ t('nav.subtitle') }}</span>
      </div>
    </div>

    <!-- Nav links -->
    <nav class="sidebar-nav">
      <router-link
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        class="nav-link"
        :class="{
          'nav-link--active': item.to === '/'
            ? $route.path === '/'
            : $route.path.startsWith(item.to)
        }"
        :title="effectiveCollapsed ? t(item.labelKey) : undefined"
        @click="closeMobile"
      >
        <span class="nav-icon" v-html="item.icon"></span>
        <span v-if="!effectiveCollapsed" class="nav-label">{{ t(item.labelKey) }}</span>
      </router-link>
    </nav>

    <!-- Footer: Language + Profile + Collapse -->
    <div class="sidebar-footer">
      <LanguageSwitcher />
      <ProfileMenu
        @show-profile-details="$emit('show-profile-details')"
        @show-tasks="$emit('show-tasks')"
      />
      <button
        class="collapse-btn"
        @click="toggleCollapsed"
        :title="effectiveCollapsed ? 'Expand sidebar' : 'Collapse sidebar'"
      >
        <svg
          width="18"
          height="18"
          viewBox="0 0 18 18"
          fill="none"
          :style="{ transform: effectiveCollapsed ? 'rotate(180deg)' : 'none' }"
        >
          <path d="M11 4L6 9L11 14" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>
  </aside>
</template>

<script setup>
import { watch } from 'vue'
import { useRoute } from 'vue-router'
import { useSidebar } from '../composables/useSidebar'
import { useI18n } from '../composables/useI18n'
import LanguageSwitcher from './LanguageSwitcher.vue'
import ProfileMenu from './ProfileMenu.vue'

defineEmits(['show-profile-details', 'show-tasks'])

const { effectiveCollapsed, toggleCollapsed, mobileOpen, closeMobile } = useSidebar()
const { t } = useI18n()
const route = useRoute()

// Close mobile drawer on route change
watch(() => route.path, () => {
  closeMobile()
})

const navItems = [
  {
    to: '/',
    labelKey: 'nav.overview',
    icon: `<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="2.5" y="2.5" width="6" height="6" rx="1.5" stroke="currentColor" stroke-width="1.5"/>
      <rect x="11.5" y="2.5" width="6" height="6" rx="1.5" stroke="currentColor" stroke-width="1.5"/>
      <rect x="2.5" y="11.5" width="6" height="6" rx="1.5" stroke="currentColor" stroke-width="1.5"/>
      <rect x="11.5" y="11.5" width="6" height="6" rx="1.5" stroke="currentColor" stroke-width="1.5"/>
    </svg>`
  },
  {
    to: '/inventory',
    labelKey: 'nav.inventory',
    icon: `<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M3 6L10 2L17 6V14L10 18L3 14V6Z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
      <path d="M10 2V18" stroke="currentColor" stroke-width="1.5"/>
      <path d="M3 6L17 6" stroke="currentColor" stroke-width="1.5"/>
    </svg>`
  },
  {
    to: '/orders',
    labelKey: 'nav.orders',
    icon: `<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="3" y="3" width="14" height="14" rx="2" stroke="currentColor" stroke-width="1.5"/>
      <path d="M7 7H13" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      <path d="M7 10H13" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      <path d="M7 13H10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
    </svg>`
  },
  {
    to: '/restocking',
    labelKey: 'nav.restocking',
    icon: `<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M3 10C3 6.13401 6.13401 3 10 3C12.3501 3 14.4368 4.15477 15.7321 5.9375" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      <path d="M17 10C17 13.866 13.866 17 10 17C7.64986 17 5.56317 15.8452 4.26795 14.0625" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      <path d="M13 6H16.5V2.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M7 14H3.5V17.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`
  },
  {
    to: '/spending',
    labelKey: 'nav.finance',
    icon: `<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="10" cy="10" r="7.5" stroke="currentColor" stroke-width="1.5"/>
      <path d="M10 6V7.5M10 12.5V14M10 7.5C8.89543 7.5 8 8.17157 8 9C8 9.82843 8.89543 10.5 10 10.5C11.1046 10.5 12 11.1716 12 12C12 12.8284 11.1046 13.5 10 13.5C8.89543 13.5 8 12.8284 8 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
    </svg>`
  },
  {
    to: '/demand',
    labelKey: 'nav.demandForecast',
    icon: `<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M2.5 14.5L7.5 9L11.5 12L17.5 5.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M14.5 5.5H17.5V8.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`
  },
  {
    to: '/reports',
    labelKey: 'nav.reports',
    icon: `<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="3" y="3" width="14" height="14" rx="2" stroke="currentColor" stroke-width="1.5"/>
      <path d="M7 13V11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      <path d="M10 13V9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      <path d="M13 13V7" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
    </svg>`
  }
]
</script>

<style scoped>
.sidebar-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  z-index: 199;
  display: none;
}

.sidebar {
  width: 248px;
  min-width: 248px;
  height: 100vh;
  background: #ffffff;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  position: sticky;
  top: 0;
  align-self: flex-start;
  transition: width 200ms ease, min-width 200ms ease;
  overflow: hidden;
  z-index: 200;
  flex-shrink: 0;
}

.sidebar--collapsed {
  width: 72px;
  min-width: 72px;
}

/* Logo */
.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.25rem 1rem;
  border-bottom: 1px solid #e2e8f0;
  flex-shrink: 0;
  min-height: 64px;
}

.logo-mark {
  width: 36px;
  height: 36px;
  min-width: 36px;
  border-radius: 9px;
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.125rem;
  font-weight: 800;
  letter-spacing: -0.025em;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.35);
  flex-shrink: 0;
}

.logo-text {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}

.logo-company {
  font-size: 0.9rem;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.02em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.logo-subtitle {
  font-size: 0.7rem;
  color: #94a3b8;
  font-weight: 400;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Nav */
.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: 0.75rem 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.sidebar-nav::-webkit-scrollbar {
  width: 3px;
}

.sidebar-nav::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-nav::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 2px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 0.875rem;
  border-radius: 8px;
  text-decoration: none;
  color: #64748b;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 200ms ease;
  white-space: nowrap;
  overflow: hidden;
  position: relative;
}

.nav-link:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.nav-link--active {
  background: #eef2ff;
  color: #4f46e5;
  font-weight: 600;
}

.nav-link--active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 60%;
  background: #6366f1;
  border-radius: 0 3px 3px 0;
}

.nav-icon {
  display: flex;
  align-items: center;
  flex-shrink: 0;
  width: 20px;
  height: 20px;
}

.nav-label {
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Collapsed nav: center icons */
.sidebar--collapsed .nav-link {
  justify-content: center;
  padding: 0.625rem;
}

.sidebar--collapsed .nav-link::before {
  left: 0;
  top: 50%;
  width: 3px;
  height: 60%;
}

/* Footer */
.sidebar-footer {
  padding: 0.5rem;
  border-top: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  flex-shrink: 0;
}

.collapse-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem;
  background: none;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  color: #64748b;
  cursor: pointer;
  transition: all 200ms ease;
  font-family: inherit;
  width: 100%;
}

.collapse-btn svg {
  transition: transform 200ms ease;
}

.collapse-btn:hover {
  background: #eef2ff;
  border-color: #c7d2fe;
  color: #4f46e5;
}

/* Mobile */
@media (max-width: 768px) {
  .sidebar-backdrop {
    display: block;
  }

  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    width: 280px !important;
    min-width: 280px !important;
    transform: translateX(-100%);
    transition: transform 200ms ease;
    z-index: 200;
    box-shadow: 4px 0 24px rgba(0, 0, 0, 0.12);
  }

  .sidebar--mobile-open {
    transform: translateX(0);
  }

  .collapse-btn {
    display: none;
  }
}
</style>
