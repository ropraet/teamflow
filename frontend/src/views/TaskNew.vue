<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { createTask, getUsers } from '../composables/api.js'
import { isBugActive } from '../composables/bugs.js'

const props = defineProps({ id: [String, Number] })
const router = useRouter()

const title = ref('')
const description = ref('')
const status = ref('todo')
const priority = ref('medium')
const assigneeId = ref(null)
const dueDate = ref('')
const users = ref([])
const error = ref('')
const submitting = ref(false)

onMounted(async () => {
  try { users.value = await getUsers() } catch {}
})

async function submit() {
  if (submitting.value) return
  // BUG: crud_create_duplicate_on_doubleclick — no debounce when active
  if (!isBugActive('crud_create_duplicate_on_doubleclick')) {
    submitting.value = true
  }
  error.value = ''
  try {
    const task = await createTask(props.id, {
      title: title.value,
      description: description.value,
      status: status.value,
      priority: priority.value,
      assignee_id: assigneeId.value ? parseInt(assigneeId.value) : null,
      due_date: dueDate.value || null,
    })
    // BUG: form_submit_no_feedback — no success message when active
    if (!isBugActive('form_submit_no_feedback') && task.message) {
      // Brief flash of success
    }
    router.push(`/projects/${props.id}/tasks`)
  } catch (e) {
    error.value = e.message
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="max-w-2xl mx-auto">
    <div class="flex items-center gap-3 mb-6">
      <button @click="router.push(`/projects/${id}/tasks`)" class="text-gray-400 hover:text-gray-600">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
      </button>
      <h1 class="text-2xl font-bold text-gray-900">New Task</h1>
    </div>

    <div class="bg-white rounded-lg border p-6">
      <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">{{ error }}</div>

      <div class="space-y-4">
        <div>
          <label for="task-title" class="block text-sm font-medium text-gray-700 mb-1">Title</label>
          <input id="task-title" v-model="title" type="text" placeholder="Task title" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 outline-none" />
        </div>
        <div>
          <label for="task-desc" class="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <textarea id="task-desc" v-model="description" rows="3" placeholder="Describe the task..." class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 outline-none resize-none"></textarea>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select v-model="status" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 outline-none">
              <option value="todo">To Do</option>
              <option value="in_progress">In Progress</option>
              <option value="done">Done</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Priority</label>
            <select v-model="priority" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 outline-none">
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Assignee</label>
            <select v-model="assigneeId" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 outline-none">
              <option :value="null">Unassigned</option>
              <option v-for="u in users" :key="u.id" :value="u.id">{{ u.name }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Due Date</label>
            <input v-model="dueDate" type="date" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 outline-none" />
          </div>
        </div>
      </div>

      <div class="mt-6 pt-4 border-t flex justify-end gap-3">
        <button @click="router.push(`/projects/${id}/tasks`)" class="px-4 py-2 border rounded-lg text-sm hover:bg-gray-50">Cancel</button>
        <button @click="submit" :disabled="submitting && !isBugActive('crud_create_duplicate_on_doubleclick')" class="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 disabled:opacity-50">
          {{ submitting ? 'Creating...' : 'Create Task' }}
        </button>
      </div>
    </div>
  </div>
</template>
