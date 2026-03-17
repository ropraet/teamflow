<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getProject } from '../composables/api.js'

const props = defineProps({ id: [String, Number] })
const router = useRouter()
const project = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    project.value = await getProject(props.id)
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
    </div>

    <div v-else-if="project">
      <div class="flex items-center gap-3 mb-6">
        <button @click="router.push('/projects')" class="text-gray-400 hover:text-gray-600">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
        </button>
        <div class="w-4 h-4 rounded-full" :style="{ backgroundColor: project.color }"></div>
        <h1 class="text-2xl font-bold text-gray-900">{{ project.title }}</h1>
        <span class="px-2.5 py-0.5 rounded-full text-xs" :class="project.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'">
          {{ project.status }}
        </span>
      </div>

      <p class="text-gray-600 mb-6">{{ project.description }}</p>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div class="bg-white rounded-lg border p-4">
          <div class="text-sm text-gray-500">Tasks</div>
          <div class="text-2xl font-bold">{{ project.task_count || 0 }}</div>
        </div>
        <div class="bg-white rounded-lg border p-4">
          <div class="text-sm text-gray-500">Completed</div>
          <div class="text-2xl font-bold text-green-600">{{ project.completed_count || 0 }}</div>
        </div>
        <div class="bg-white rounded-lg border p-4">
          <div class="text-sm text-gray-500">Members</div>
          <div class="text-2xl font-bold">{{ project.member_count || 0 }}</div>
        </div>
      </div>

      <div class="flex gap-3">
        <router-link :to="`/projects/${id}/tasks`" class="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700">
          View Tasks
        </router-link>
        <router-link :to="`/projects/${id}/team`" class="px-4 py-2 border rounded-lg text-sm font-medium hover:bg-gray-50">
          Team
        </router-link>
        <router-link :to="`/projects/${id}/export`" class="px-4 py-2 border rounded-lg text-sm font-medium hover:bg-gray-50">
          Export
        </router-link>
        <router-link :to="`/projects/${id}/settings`" class="px-4 py-2 border rounded-lg text-sm font-medium hover:bg-gray-50">
          Settings
        </router-link>
      </div>
    </div>

    <div v-else class="text-center py-20 text-gray-400">Project not found</div>
  </div>
</template>
