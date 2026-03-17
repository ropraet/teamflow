<script setup>
import { ref } from 'vue'
import { login, getActiveBugs } from '../composables/api.js'

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)
const showPassword = ref(false)

async function handleSubmit() {
  error.value = ''
  if (!email.value || !password.value) {
    error.value = 'Please fill in all fields'
    return
  }
  loading.value = true
  try {
    const data = await login(email.value, password.value)
    localStorage.setItem('teamflow_token', data.token)
    localStorage.setItem('teamflow_user', JSON.stringify(data.user))
    window.location.href = '/dashboard'
  } catch (e) {
    error.value = e.message || 'Login failed'
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
      <h2 class="mt-6 text-center text-3xl font-bold text-gray-900">Sign in to TeamFlow</h2>
      <p class="mt-2 text-center text-sm text-gray-600">
        Or <router-link to="/register" class="font-medium text-primary-600 hover:text-primary-500">create a new account</router-link>
      </p>
    </div>

    <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
      <div class="bg-white py-8 px-4 shadow-lg sm:rounded-xl sm:px-10 border border-gray-100">
        <div v-if="error" class="mb-6 rounded-lg bg-red-50 border border-red-200 p-4">
          <p class="text-sm text-red-700">{{ error }}</p>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-6">
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700">Email address</label>
            <input id="email" v-model="email" type="email" autocomplete="email" required placeholder="you@example.com" class="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2.5 shadow-sm focus:ring-2 focus:ring-primary-600 focus:border-transparent outline-none sm:text-sm" />
          </div>

          <div>
            <label for="password" class="block text-sm font-medium text-gray-700">Password</label>
            <div class="mt-1 relative">
              <input id="password" v-model="password" :type="showPassword ? 'text' : 'password'" autocomplete="current-password" required placeholder="Enter your password" class="block w-full rounded-lg border border-gray-300 px-3 py-2.5 pr-10 shadow-sm focus:ring-2 focus:ring-primary-600 focus:border-transparent outline-none sm:text-sm" />
              <button type="button" @click="showPassword = !showPassword" class="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600">
                <span class="text-xs">{{ showPassword ? 'Hide' : 'Show' }}</span>
              </button>
            </div>
          </div>

          <div class="flex items-center justify-end">
            <router-link to="/forgot-password" class="text-sm font-medium text-primary-600 hover:text-primary-500">Forgot your password?</router-link>
          </div>

          <button type="submit" :disabled="loading" class="flex w-full justify-center rounded-lg bg-primary-600 px-3 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 disabled:opacity-50 transition-colors">
            {{ loading ? 'Signing in...' : 'Sign in' }}
          </button>
        </form>

        <div class="mt-6 border-t pt-4">
          <p class="text-center text-xs text-gray-500">Demo accounts: admin@teamflow.dev / admin123 or member@teamflow.dev / member123</p>
        </div>
      </div>
    </div>
  </div>
</template>
