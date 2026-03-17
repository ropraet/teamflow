<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getProject, updateProject, deleteProject } from '../composables/api.js'

const props = defineProps({ id: [String, Number] })
const router = useRouter()
const project = ref(null)
const title = ref('')
const description = ref('')
const status = ref('active')
const saving = ref(false)
const message = ref('')

onMounted(async () => {
  try {
    project.value = await getProject(props.id)
    title.value = project.value.title
    description.value = project.value.description
    status.value = project.value.status
  } catch (e) {
    console.error(e)
  }
})

async function save() {
  saving.value = true
  message.value = ''
  try {
    await updateProject(props.id, { title: title.value, description: description.value, status: status.value })
    message.value = 'Settings saved!'
  } catch (e) {
    message.value = e.message
  } finally {
    saving.value = false
  }
}

async function handleDelete() {
  if (!confirm('Delete this project? This cannot be undone.')) return
  try {
    await deleteProject(props.id)
    router.push('/projects')
  } catch (e) {
    alert(e.message)
  }
}
</script>

<template>
  <div class="max-w-2xl mx-auto">
    <div class="flex items-center gap-3 mb-6">
      <button @click="router.push(`/projects/${id}`)" class="text-gray-400 hover:text-gray-600">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
      </button>
      <h1 class="text-2xl font-bold text-gray-900">Project Settings</h1>
    </div>

    <div v-if="project" class="space-y-6">
      <div class="bg-white rounded-lg border p-6">
        <h2 class="text-lg font-semibold mb-4">General</h2>
        <div v-if="message" class="mb-4 p-3 rounded-lg text-sm" :class="message.includes('saved') ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-600'">{{ message }}</div>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Title</label>
            <input v-model="title" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 outline-none" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea v-model="description" rows="3" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 outline-none resize-none"></textarea>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select v-model="status" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 outline-none">
              <option value="active">Active</option>
              <option value="completed">Completed</option>
              <option value="archived">Archived</option>
            </select>
          </div>
          <button @click="save" :disabled="saving" class="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 disabled:opacity-50">
            {{ saving ? 'Saving...' : 'Save Changes' }}
          </button>
        </div>
      </div>

      <div class="bg-white rounded-lg border border-red-200 p-6">
        <h2 class="text-lg font-semibold text-red-600 mb-2">Danger Zone</h2>
        <p class="text-sm text-gray-500 mb-4">Once you delete a project, there is no going back.</p>
        <button @click="handleDelete" class="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700">
          Delete Project
        </button>
      </div>
    </div>
  </div>
</template>
