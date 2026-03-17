<script setup>
import { ref, onMounted } from 'vue'
import { getDashboard } from '../composables/api.js'
import { isBugActive, loadBugs } from '../composables/bugs.js'

const data = ref(null)
const loading = ref(true)

onMounted(async () => {
  await loadBugs()
  try {
    data.value = await getDashboard()
  } catch (e) {
    console.error('Failed to load dashboard', e)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <!-- BUG: seo_duplicate_h1 — two H1 tags when bug active -->
    <h1 class="text-2xl font-bold text-gray-900 mb-6">Dashboard</h1>
    <h1 v-if="isBugActive('seo_duplicate_h1')" class="text-xl font-semibold text-gray-700 mb-4">Welcome back!</h1>
    <p v-else class="text-gray-500 mb-6">Welcome back! Here's your overview.</p>

    <!-- BUG: loading_state_missing — no spinner when bug active -->
    <div v-if="loading && !isBugActive('loading_state_missing')" class="flex items-center justify-center py-20">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
    </div>

    <div v-if="data" class="space-y-6">
      <!-- Stats cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-white rounded-lg border p-5">
          <div class="text-sm font-medium" :class="isBugActive('a11y_low_contrast') ? 'text-gray-300' : 'text-gray-500'">Total Projects</div>
          <div class="text-3xl font-bold text-gray-900 mt-1">{{ data.projects }}</div>
        </div>
        <div class="bg-white rounded-lg border p-5">
          <div class="text-sm font-medium" :class="isBugActive('a11y_low_contrast') ? 'text-gray-300' : 'text-gray-500'">Total Tasks</div>
          <div class="text-3xl font-bold text-gray-900 mt-1">{{ data.tasks?.total || 0 }}</div>
        </div>
        <div class="bg-white rounded-lg border p-5">
          <div class="text-sm font-medium" :class="isBugActive('a11y_low_contrast') ? 'text-gray-300' : 'text-gray-500'">Completed</div>
          <div class="text-3xl font-bold text-green-600 mt-1">{{ data.tasks?.completed || 0 }}</div>
        </div>
        <div class="bg-white rounded-lg border p-5">
          <div class="text-sm font-medium" :class="isBugActive('a11y_low_contrast') ? 'text-gray-300' : 'text-gray-500'">Overdue</div>
          <div class="text-3xl font-bold text-red-600 mt-1">{{ data.tasks?.overdue || 0 }}</div>
        </div>
      </div>

      <!-- Task status breakdown -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="bg-white rounded-lg border p-5">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Task Status</h2>
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-600">To Do</span>
              <span class="text-sm font-medium px-2.5 py-0.5 bg-gray-100 rounded-full">{{ data.tasks?.todo || 0 }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-600">In Progress</span>
              <span class="text-sm font-medium px-2.5 py-0.5 bg-blue-100 text-blue-700 rounded-full">{{ data.tasks?.in_progress || 0 }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-600">Done</span>
              <span class="text-sm font-medium px-2.5 py-0.5 bg-green-100 text-green-700 rounded-full">{{ data.tasks?.completed || 0 }}</span>
            </div>
          </div>
        </div>

        <!-- Recent Activity -->
        <div class="bg-white rounded-lg border p-5">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h2>
          <div class="space-y-3">
            <div v-for="a in data.recent_activity" :key="a.id" class="flex items-start gap-3 text-sm">
              <div class="w-8 h-8 rounded-full bg-primary-100 text-primary-600 flex items-center justify-center text-xs font-medium flex-shrink-0">
                {{ a.user_name?.[0] || '?' }}
              </div>
              <div>
                <span class="font-medium text-gray-900">{{ a.user_name }}</span>
                <span class="text-gray-500 ml-1">{{ a.details }}</span>
              </div>
            </div>
            <div v-if="!data.recent_activity?.length" class="text-sm text-gray-400">No recent activity</div>
          </div>
        </div>
      </div>

      <!-- BUG: img_missing_alt — image without alt when bug active -->
      <div v-if="isBugActive('img_missing_alt')" class="bg-white rounded-lg border p-5">
        <img src="https://placehold.co/800x200/e2e8f0/94a3b8?text=TeamFlow+Banner" class="w-full rounded">
      </div>
    </div>
  </div>
</template>
