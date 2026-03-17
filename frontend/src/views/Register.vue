<script setup>
import { ref } from 'vue'
import { register } from '../composables/api.js'

const name = ref('')
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleSubmit() {
  error.value = ''
  if (!name.value || !email.value || !password.value) {
    error.value = 'Please fill in all fields'
    return
  }
  loading.value = true
  try {
    const data = await register(email.value, name.value, password.value)
    localStorage.setItem('teamflow_token', data.token)
    localStorage.setItem('teamflow_user', JSON.stringify(data.user))
    window.location.href = '/dashboard'
  } catch (e) {
    error.value = e.message || 'Registration failed'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <div class="flex justify-center">
        <div class="h-12 w-12 rounded-xl bg-primary-600 flex items-center justify-center">
          <span class="text-white font-bold text-lg">TF</span>
        </div>
      </div>
      <h2 class="mt-6 text-center text-3xl font-bold text-gray-900">Create your account</h2>
      <p class="mt-2 text-center text-sm text-gray-600">
        Already have an account? <router-link to="/login" class="font-medium text-primary-600 hover:text-primary-500">Sign in</router-link>
      </p>
    </div>

    <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
      <div class="bg-white py-8 px-4 shadow-lg sm:rounded-xl sm:px-10 border border-gray-100">
        <div v-if="error" class="mb-6 rounded-lg bg-red-50 border border-red-200 p-4">
          <p class="text-sm text-red-700">{{ error }}</p>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-5">
          <div>
            <label for="name" class="block text-sm font-medium text-gray-700">Full name</label>
            <input id="name" v-model="name" type="text" autocomplete="name" required placeholder="Jane Smith" class="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2.5 shadow-sm focus:ring-2 focus:ring-primary-600 focus:border-transparent outline-none sm:text-sm" />
          </div>
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700">Email address</label>
            <input id="email" v-model="email" type="email" autocomplete="email" required placeholder="you@example.com" class="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2.5 shadow-sm focus:ring-2 focus:ring-primary-600 focus:border-transparent outline-none sm:text-sm" />
          </div>
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700">Password</label>
            <input id="password" v-model="password" type="password" autocomplete="new-password" required placeholder="Min 6 characters" class="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2.5 shadow-sm focus:ring-2 focus:ring-primary-600 focus:border-transparent outline-none sm:text-sm" />
          </div>

          <button type="submit" :disabled="loading" class="flex w-full justify-center rounded-lg bg-primary-600 px-3 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 disabled:opacity-50 transition-colors">
            {{ loading ? 'Creating account...' : 'Create account' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>
