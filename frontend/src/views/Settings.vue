<script setup>
import { ref, onMounted } from 'vue'
import { getMe, updateProfile, getNotifications, updateNotifications } from '../composables/api.js'
import { isBugActive } from '../composables/bugs.js'

const tab = ref('profile')
const name = ref('')
const email = ref('')
const saving = ref(false)
const message = ref('')
const error = ref('')

// Notifications
const notifications = ref({})

onMounted(async () => {
  try {
    const user = await getMe()
    name.value = user.name
    email.value = user.email
    const notifs = await getNotifications()
    notifications.value = notifs
  } catch (e) {
    console.error(e)
  }
})

async function saveProfile() {
  saving.value = true
  error.value = ''
  message.value = ''
  try {
    await updateProfile({ name: name.value, email: email.value })
    message.value = 'Profile updated!'
    // Update stored user
    const stored = JSON.parse(localStorage.getItem('teamflow_user') || '{}')
    stored.name = name.value
    stored.email = email.value
    localStorage.setItem('teamflow_user', JSON.stringify(stored))
  } catch (e) {
    error.value = e.message
  } finally {
    saving.value = false
  }
}

async function saveNotifications() {
  saving.value = true
  try {
    await updateNotifications(notifications.value)
    message.value = 'Notifications updated!'
  } catch (e) {
    error.value = e.message
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="max-w-2xl mx-auto">
    <h1 class="text-2xl font-bold text-gray-900 mb-6">Settings</h1>

    <!-- Tabs -->
    <div class="flex gap-1 mb-6 border-b">
      <button
        @click="tab = 'profile'"
        class="px-4 py-2 text-sm font-medium border-b-2 -mb-px"
        :class="tab === 'profile' ? 'border-primary-600 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700'"
      >Profile</button>
      <button
        @click="tab = 'notifications'"
        class="px-4 py-2 text-sm font-medium border-b-2 -mb-px"
        :class="tab === 'notifications' ? 'border-primary-600 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700'"
      >Notifications</button>
    </div>

    <div v-if="message" class="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg text-sm text-green-600">{{ message }}</div>
    <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">{{ error }}</div>

    <!-- Profile tab -->
    <div v-if="tab === 'profile'" class="bg-white rounded-lg border p-6">
      <h2 class="text-lg font-semibold mb-4">Profile Information</h2>
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Name</label>
          <input v-model="name" type="text" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 outline-none" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <input v-model="email" type="email" class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 outline-none" />
          <!-- BUG hint: form_accepts_invalid_email — no frontend validation -->
        </div>
        <button @click="saveProfile" :disabled="saving" class="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 disabled:opacity-50">
          {{ saving ? 'Saving...' : 'Save Profile' }}
        </button>
      </div>
    </div>

    <!-- Notifications tab -->
    <div v-if="tab === 'notifications'" class="bg-white rounded-lg border p-6">
      <h2 class="text-lg font-semibold mb-4">Notification Preferences</h2>
      <div class="space-y-4">
        <label class="flex items-center gap-3 cursor-pointer">
          <input type="checkbox" v-model="notifications.email_notifications" class="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500" />
          <div>
            <div class="text-sm font-medium text-gray-700">Email Notifications</div>
            <div class="text-xs text-gray-400">Receive email updates about your tasks and projects</div>
          </div>
        </label>
        <label class="flex items-center gap-3 cursor-pointer">
          <input type="checkbox" v-model="notifications.push_notifications" class="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500" />
          <div>
            <div class="text-sm font-medium text-gray-700">Push Notifications</div>
            <div class="text-xs text-gray-400">Get browser push notifications for urgent updates</div>
          </div>
        </label>
        <label class="flex items-center gap-3 cursor-pointer">
          <input type="checkbox" v-model="notifications.weekly_digest" class="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500" />
          <div>
            <div class="text-sm font-medium text-gray-700">Weekly Digest</div>
            <div class="text-xs text-gray-400">Receive a weekly summary of project activity</div>
          </div>
        </label>
        <label class="flex items-center gap-3 cursor-pointer">
          <input type="checkbox" v-model="notifications.mention_alerts" class="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500" />
          <div>
            <div class="text-sm font-medium text-gray-700">Mention Alerts</div>
            <div class="text-xs text-gray-400">Get notified when someone mentions you</div>
          </div>
        </label>
        <button @click="saveNotifications" :disabled="saving" class="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 disabled:opacity-50">
          {{ saving ? 'Saving...' : 'Save Preferences' }}
        </button>
      </div>
    </div>
  </div>
</template>
