<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useBugs } from './composables/bugs.js'

const router = useRouter()
const route = useRoute()
const { isBugActive, loadBugs } = useBugs()

const user = ref(null)
const sidebarOpen = ref(true)

const isPublicPage = computed(() => route.meta?.public)

onMounted(async () => {
  await loadBugs()
  const stored = localStorage.getItem('teamflow_user')
  if (stored) user.value = JSON.parse(stored)
})

watch(() => route.path, () => {
  const stored = localStorage.getItem('teamflow_user')
  if (stored) user.value = JSON.parse(stored)
})

function handleLogout() {
  if (!isBugActive('auth_session_not_cleared')) {
    localStorage.removeItem('teamflow_token')
    localStorage.removeItem('teamflow_user')
  } else {
    // BUG: only remove cookie, not localStorage
    document.cookie = 'teamflow_token=; Max-Age=0; path=/'
  }
  router.push('/login')
}

const navItems = [
  { label: 'Dashboard', path: '/dashboard', icon: '&#9638;' },
  { label: 'Projects', path: '/projects', icon: '&#128193;' },
  { label: 'Reports', path: '/reports', icon: '&#128200;' },
  { label: 'Settings', path: '/settings/profile', icon: '&#9881;' },
]
</script>

<template>
  <div v-if="isPublicPage">
    <router-view />
  </div>
  <div v-else class="flex h-screen overflow-hidden">
    <!-- Sidebar -->
    <aside
      class="bg-gray-900 text-white flex flex-col transition-all duration-200"
      :class="[
        sidebarOpen ? 'w-64' : 'w-16',
        isBugActive('responsive_sidebar_overlap') ? 'fixed z-50 h-full md:relative' : 'relative'
      ]"
    >
      <div class="p-4 flex items-center gap-3 border-b border-gray-800">
        <div class="w-8 h-8 bg-primary-500 rounded-lg flex items-center justify-center font-bold text-sm">TF</div>
        <span v-if="sidebarOpen" class="font-semibold text-lg">TeamFlow</span>
      </div>
      <nav class="flex-1 py-4">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="flex items-center gap-3 px-4 py-2.5 text-gray-300 hover:bg-gray-800 hover:text-white transition-colors"
          :class="{ 'bg-gray-800 text-white': route.path.startsWith(item.path) }"
        >
          <span class="w-5 text-center" v-html="item.icon"></span>
          <span v-if="sidebarOpen">{{ item.label }}</span>
        </router-link>
        <!-- External docs link -->
        <a
          v-if="isBugActive('broken_external_link')"
          href="https://docs.teamflow.app"
          target="_blank"
          class="flex items-center gap-3 px-4 py-2.5 text-gray-300 hover:bg-gray-800 hover:text-white transition-colors"
        >
          <span class="w-5 text-center">&#128214;</span>
          <span v-if="sidebarOpen">Documentation</span>
        </a>
      </nav>
      <div class="p-4 border-t border-gray-800">
        <div v-if="sidebarOpen && user" class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center text-sm font-medium">
            {{ user.name?.[0] || 'U' }}
          </div>
          <div class="flex-1 min-w-0">
            <div class="text-sm font-medium truncate">{{ user.name }}</div>
            <div class="text-xs text-gray-400 truncate">{{ user.role }}</div>
          </div>
        </div>
        <button
          @click="handleLogout"
          class="mt-3 w-full text-left px-2 py-1.5 text-sm text-gray-400 hover:text-white transition-colors"
          :class="{ 'text-center': !sidebarOpen }"
        >
          {{ sidebarOpen ? 'Logout' : '&#x2192;' }}
        </button>
      </div>
    </aside>

    <!-- Main content -->
    <main class="flex-1 overflow-y-auto">
      <header class="bg-white border-b px-6 py-3 flex items-center justify-between sticky top-0 z-10">
        <button @click="sidebarOpen = !sidebarOpen" class="p-1.5 rounded hover:bg-gray-100">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
        </button>
        <div class="flex items-center gap-4">
          <span v-if="user" class="text-sm text-gray-500">{{ user.email }}</span>
        </div>
      </header>
      <div class="p-6">
        <router-view />
      </div>
    </main>
  </div>
</template>
