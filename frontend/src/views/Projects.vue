<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getProjects, deleteProject } from '../composables/api.js'
import { isBugActive } from '../composables/bugs.js'

const router = useRouter()
const projects = ref([])
const loading = ref(true)

async function load() {
  loading.value = true
  try {
    projects.value = await getProjects()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function handleDelete(id) {
  if (!confirm('Are you sure you want to delete this project?')) return
  try {
    await deleteProject(id)
    // BUG: crud_delete_item_reappears — if bug active, item stays in list
    if (!isBugActive('crud_delete_item_reappears')) {
      projects.value = projects.value.filter(p => p.id !== id)
    }
  } catch (e) {
    alert(e.message)
  }
}

onMounted(load)
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-gray-900">Projects</h1>
      <router-link to="/projects/new" class="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
        + New Project
      </router-link>
    </div>

    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="p in projects"
        :key="p.id"
        class="bg-white rounded-lg border hover:shadow-md transition-shadow cursor-pointer"
        @click="router.push(`/projects/${p.id}`)"
      >
        <div class="p-5">
          <div class="flex items-center gap-2 mb-2">
            <div class="w-3 h-3 rounded-full" :style="{ backgroundColor: p.color }"></div>
            <h3 class="font-semibold text-gray-900">{{ p.title }}</h3>
          </div>
          <p class="text-sm text-gray-500 line-clamp-2 mb-4">{{ p.description || 'No description' }}</p>
          <div class="flex items-center justify-between text-xs text-gray-400">
            <div class="flex items-center gap-3">
              <span>{{ p.task_count || 0 }} tasks</span>
              <span>{{ p.member_count || 0 }} members</span>
            </div>
            <span class="px-2 py-0.5 rounded-full text-xs" :class="p.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'">
              {{ p.status }}
            </span>
          </div>
          <div v-if="p.task_count > 0" class="mt-3 w-full bg-gray-200 rounded-full h-1.5">
            <div class="bg-green-500 h-1.5 rounded-full" :style="{ width: ((p.completed_count || 0) / p.task_count * 100) + '%' }"></div>
          </div>
        </div>
        <div class="border-t px-5 py-2.5 flex justify-end gap-2" @click.stop>
          <button @click="router.push(`/projects/${p.id}/tasks`)" class="text-xs text-primary-600 hover:text-primary-800">Tasks</button>
          <button @click="router.push(`/projects/${p.id}/team`)" class="text-xs text-primary-600 hover:text-primary-800">Team</button>
          <button @click="handleDelete(p.id)" class="text-xs text-red-500 hover:text-red-700">Delete</button>
        </div>
      </div>
    </div>

    <div v-if="!loading && projects.length === 0" class="text-center py-20 text-gray-400">
      <p class="text-lg mb-2">No projects yet</p>
      <router-link to="/projects/new" class="text-primary-600 hover:text-primary-800">Create your first project</router-link>
    </div>
  </div>
</template>
