<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { exportCSV, exportJSON } from '../composables/api.js'

const props = defineProps({ id: [String, Number] })
const router = useRouter()
const downloading = ref('')

async function downloadCSV() {
  downloading.value = 'csv'
  try {
    const res = await exportCSV(props.id)
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `project_${props.id}_tasks.csv`
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    alert(e.message)
  } finally {
    downloading.value = ''
  }
}

async function downloadJSON() {
  downloading.value = 'json'
  try {
    const res = await exportJSON(props.id)
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `project_${props.id}_tasks.json`
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    alert(e.message)
  } finally {
    downloading.value = ''
  }
}
</script>

<template>
  <div class="max-w-2xl mx-auto">
    <div class="flex items-center gap-3 mb-6">
      <button @click="router.push(`/projects/${id}`)" class="text-gray-400 hover:text-gray-600">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
      </button>
      <h1 class="text-2xl font-bold text-gray-900">Export Tasks</h1>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div class="bg-white rounded-lg border p-6">
        <div class="text-center">
          <div class="text-4xl mb-3">&#128196;</div>
          <h2 class="text-lg font-semibold mb-2">CSV Export</h2>
          <p class="text-sm text-gray-500 mb-4">Download all tasks as a CSV spreadsheet file. Compatible with Excel, Google Sheets, etc.</p>
          <button
            @click="downloadCSV"
            :disabled="!!downloading"
            class="px-6 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 disabled:opacity-50"
          >
            {{ downloading === 'csv' ? 'Downloading...' : 'Download CSV' }}
          </button>
        </div>
      </div>

      <div class="bg-white rounded-lg border p-6">
        <div class="text-center">
          <div class="text-4xl mb-3">&#123; &#125;</div>
          <h2 class="text-lg font-semibold mb-2">JSON Export</h2>
          <p class="text-sm text-gray-500 mb-4">Download all tasks as a JSON file. Useful for programmatic processing and integrations.</p>
          <button
            @click="downloadJSON"
            :disabled="!!downloading"
            class="px-6 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 disabled:opacity-50"
          >
            {{ downloading === 'json' ? 'Downloading...' : 'Download JSON' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
