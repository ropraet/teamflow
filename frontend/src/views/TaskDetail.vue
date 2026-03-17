<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getTask, deleteTask } from '../composables/api.js'

const props = defineProps({ id: [String, Number], taskId: [String, Number] })
const router = useRouter()
const task = ref(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    task.value = await getTask(props.taskId)
    // Parse labels safely
    if (typeof task.value.labels === 'string') {
      try {
        task.value.labels = JSON.parse(task.value.labels)
      } catch (e) {
        // BUG: console_unhandled_error — this will throw when labels is invalid JSON
        console.error('Failed to parse labels:', e)
        task.value.labels = []
      }
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})

async function handleDelete() {
  if (!confirm('Delete this task?')) return
  try {
    await deleteTask(props.taskId)
    router.push(`/projects/${props.id}/tasks`)
  } catch (e) {
    alert(e.message)
  }
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
</script>

<template>
  <div class="max-w-3xl mx-auto">
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
    </div>

    <div v-else-if="error" class="text-center py-20 text-red-500">{{ error }}</div>

    <div v-else-if="task">
      <div class="flex items-center gap-3 mb-6">
        <button @click="router.push(`/projects/${id}/tasks`)" class="text-gray-400 hover:text-gray-600">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
        </button>
        <h1 class="text-2xl font-bold text-gray-900">{{ task.title }}</h1>
      </div>

      <div class="bg-white rounded-lg border p-6">
        <div class="flex items-center gap-3 mb-4">
          <span class="px-2.5 py-1 rounded-full text-xs font-medium" :class="statusColor[task.status]">
            {{ task.status?.replace('_', ' ') }}
          </span>
          <span class="px-2.5 py-1 rounded-full text-xs font-medium" :class="priorityColor[task.priority]">
            {{ task.priority }}
          </span>
        </div>

        <div v-if="task.description" class="mb-6">
          <h3 class="text-sm font-medium text-gray-500 mb-1">Description</h3>
          <p class="text-gray-700">{{ task.description }}</p>
        </div>

        <div class="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span class="text-gray-500">Assignee:</span>
            <span class="ml-2 text-gray-900">{{ task.assignee_name || 'Unassigned' }}</span>
          </div>
          <div>
            <span class="text-gray-500">Due Date:</span>
            <span class="ml-2 text-gray-900">{{ task.due_date || 'No due date' }}</span>
          </div>
          <div>
            <span class="text-gray-500">Created:</span>
            <span class="ml-2 text-gray-900">{{ task.created_at }}</span>
          </div>
          <div>
            <span class="text-gray-500">Updated:</span>
            <span class="ml-2 text-gray-900">{{ task.updated_at }}</span>
          </div>
        </div>

        <div v-if="Array.isArray(task.labels) && task.labels.length" class="mt-4">
          <span class="text-sm text-gray-500">Labels:</span>
          <div class="flex gap-1 mt-1">
            <span v-for="label in task.labels" :key="label" class="px-2 py-0.5 bg-primary-100 text-primary-700 rounded-full text-xs">
              {{ label }}
            </span>
          </div>
        </div>

        <div class="mt-6 pt-4 border-t flex gap-3">
          <router-link :to="`/projects/${id}/tasks/${taskId}/edit`" class="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700">
            Edit
          </router-link>
          <button @click="handleDelete" class="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700">
            Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
