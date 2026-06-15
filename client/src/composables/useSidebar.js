import { ref, computed } from 'vue'

// Singleton state — module-level, shared across all component instances
const collapsed = ref(localStorage.getItem('sidebar-collapsed') === 'true')
const mobileOpen = ref(false)

// Track whether the viewport is mobile (<=768px)
const isMobile = ref(window.matchMedia('(max-width: 768px)').matches)
const _mql = window.matchMedia('(max-width: 768px)')
_mql.addEventListener('change', (e) => {
  isMobile.value = e.matches
})

// The sidebar is only visually collapsed on desktop.
// On mobile the drawer always shows full labels regardless of persisted state.
const effectiveCollapsed = computed(() => collapsed.value && !isMobile.value)

const toggleCollapsed = () => {
  collapsed.value = !collapsed.value
  localStorage.setItem('sidebar-collapsed', collapsed.value)
}

const openMobile = () => {
  mobileOpen.value = true
}

const closeMobile = () => {
  mobileOpen.value = false
}

const toggleMobile = () => {
  mobileOpen.value = !mobileOpen.value
}

export function useSidebar() {
  return {
    collapsed,
    effectiveCollapsed,
    isMobile,
    toggleCollapsed,
    mobileOpen,
    openMobile,
    closeMobile,
    toggleMobile
  }
}
