<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getTasks } from '../composables/api.js'
import { isBugActive } from '../composables/bugs.js'

const props = defineProps({ id: [String, Number] })
const router = useRouter()

const tasks = ref([])
const loading = ref(true)
const total = ref(0)
const page = ref(1)
const pages = ref(1)
const search = ref('')
const statusFilter = ref('')
const priorityFilter = ref('')
const sortBy = ref('created_at')
const sortOrder = ref('desc')

async function load() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      per_page: 10,
      sort: sortBy.value,
      order: sortOrder.value,
    }
    if (search.value) params.search = search.value
    if (statusFilter.value) params.status = statusFilter.value
    if (priorityFilter.value) params.priority = priorityFilter.value
    const data = await getTasks(props.id, params)
    tasks.value = data.tasks
    total.value = data.total
    pages.value = data.pages
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function setPage(p) {
  page.value = p
  load()
}

function applyFilters() {
  page.value = 1
  load()
}

function clearFilters() {
  search.value = ''
  statusFilter.value = ''
  priorityFilter.value = ''
  page.value = 1
  load()
}

function toggleSort(col) {
  if (sortBy.value === col) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortBy.value = col
    sortOrder.value = 'asc'
  }
  load()
}

const priorityColor = {
  critical: 'bg-red-100 text-red-700',
  high: 'bg-orange-100 text-orange-700',
  medium: 'bg-yellow-100 text-yellow-700',
  low: 'bg-gray-100 text-gray-600',
}

const statusColor = {
  todo: 'bg-gray-100 text-gray-600',
  in_progress: 'bg-blue-100 text-blue-700',
  done: 'bg-green-100 text-green-700',
}

onMounted(load)

// BUG: search_doesnt_clear — search persists (we just never clear it on mount, which is the normal case)
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-3">
        <button @click="router.push(`/projects/${id}`)" class="text-gray-400 hover:text-gray-600">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
        </button>
        <h1 class="text-2xl font-bold text-gray-900">Tasks</h1>
        <span class="text-sm text-gray-400">({{ total }})</span>
      </div>
      <router-link
        :to="`/projects/${id}/tasks/new`"
        class="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg text-sm font-medium"
      >
        + New Task
      </router-link>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg border p-4 mb-4">
      <div class="flex flex-wrap gap-3 items-center">
        <input
          v-model="search"
          @keyup.enter="applyFilters"
          placeholder="Search tasks..."
          class="px-3 py-1.5 border rounded-lg text-sm focus:ring-2 focus:ring-primary-500 outline-none w-64"
        />
        <select v-model="statusFilter" @change="applyFilters" class="px-3 py-1.5 border rounded-lg text-sm focus:ring-2 focus:ring-primary-500 outline-none">
          <option value="">All statuses</option>
          <option value="todo">To Do</option>
          <option value="in_progress">In Progress</option>
          <option value="done">Done</option>
        </select>
        <select v-model="priorityFilter" @change="applyFilters" class="px-3 py-1.5 border rounded-lg text-sm focus:ring-2 focus:ring-primary-500 outline-none">
          <option value="">All priorities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
        <button @click="applyFilters" class="px-3 py-1.5 bg-primary-600 text-white rounded-lg text-sm hover:bg-primary-700">Search</button>
        <button @click="clearFilters" class="px-3 py-1.5 text-sm text-gray-500 hover:text-gray-700">Clear</button>
      </div>
    </div>

    <!-- BUG: loading_state_missing — no spinner -->
    <div v-if="loading && !isBugActive('loading_state_missing')" class="flex items-center justify-center py-10">
      <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
    </div>

    <!-- Table -->
    <div v-else class="bg-white rounded-lg border overflow-x-auto">
      <!-- BUG: responsive_table_overflow — no responsive wrapper when active -->
      <table class="w-full" :class="{ 'min-w-[800px]': isBugActive('responsive_table_overflow') }">
        <thead>
          <tr class="border-b bg-gray-50">
            <th class="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase cursor-pointer hover:text-gray-700" @click="toggleSort('title')">
              Title {{ sortBy === 'title' ? (sortOrder === 'asc' ? '↑' : '↓') : '' }}
            </th>
            <th class="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase cursor-pointer hover:text-gray-700" @click="toggleSort('status')">
              Status {{ sortBy === 'status' ? (sortOrder === 'asc' ? '↑' : '↓') : '' }}
            </th>
            <th class="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase cursor-pointer hover:text-gray-700" @click="toggleSort('priority')">
              Priority {{ sortBy === 'priority' ? (sortOrder === 'asc' ? '↑' : '↓') : '' }}
            </th>
            <th class="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Assignee</th>
            <th class="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase cursor-pointer hover:text-gray-700" @click="toggleSort('due_date')">
              Due {{ sortBy === 'due_date' ? (sortOrder === 'asc' ? '↑' : '↓') : '' }}
            </th>
            <th class="text-left px-4 py-3 text-xs font-medium text-gray-500 uppercase">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in tasks" :key="t.id" class="border-b hover:bg-gray-50 cursor-pointer" @click="router.push(`/projects/${id}/tasks/${t.id}`)">
            <td class="px-4 py-3">
              <div class="font-medium text-gray-900 text-sm">{{ t.title }}</div>
              <div class="text-xs text-gray-400 line-clamp-1">{{ t.description }}</div>
            </td>
            <td class="px-4 py-3">
              <span class="px-2 py-0.5 rounded-full text-xs font-medium" :class="statusColor[t.status] || 'bg-gray-100'">
                {{ t.status?.replace('_', ' ') }}
              </span>
            </td>
            <td class="px-4 py-3">
              <span class="px-2 py-0.5 rounded-full text-xs font-medium" :class="priorityColor[t.priority] || 'bg-gray-100'">
                {{ t.priority }}
              </span>
            </td>
            <td class="px-4 py-3 text-sm text-gray-600">{{ t.assignee_name || '—' }}</td>
            <td class="px-4 py-3 text-sm text-gray-600">{{ t.due_date || '—' }}</td>
            <td class="px-4 py-3" @click.stop>
              <!-- BUG: responsive_button_too_small — small buttons -->
              <div class="flex gap-1">
                <button
                  @click="router.push(`/projects/${id}/tasks/${t.id}/edit`)"
                  class="text-primary-600 hover:text-primary-800"
                  :class="isBugActive('responsive_button_too_small') ? 'p-0.5 text-xs' : 'p-1.5 text-sm'"
                >Edit</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- BUG: search_no_results_state_missing — no "no results" message -->
      <div v-if="tasks.length === 0 && !isBugActive('search_no_results_state_missing')" class="text-center py-10 text-gray-400">
        <p>No tasks found</p>
        <p class="text-sm mt-1">Try adjusting your filters or search query</p>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="pages > 1" class="flex items-center justify-between mt-4">
      <div class="text-sm text-gray-500">Showing page {{ page }} of {{ pages }} ({{ total }} tasks)</div>
      <div class="flex gap-1">
        <button
          v-for="p in pages"
          :key="p"
          @click="setPage(p)"
          class="px-3 py-1 rounded text-sm"
          :class="p === page ? 'bg-primary-600 text-white' : 'bg-white border hover:bg-gray-50'"
        >{{ p }}</button>
      </div>
    </div>
  </div>
</template>
