<script setup>
import { ref } from 'vue'
import { forgotPassword } from '../composables/api.js'

const email = ref('')
const error = ref('')
const loading = ref(false)
const submitted = ref(false)

async function handleSubmit() {
  error.value = ''
  if (!email.value) { error.value = 'Email is required'; return }
  loading.value = true
  try {
    await forgotPassword(email.value)
    submitted.value = true
  } catch (e) {
    error.value = e.message
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
      <h2 class="mt-6 text-center text-3xl font-bold text-gray-900">Reset your password</h2>
      <p class="mt-2 text-center text-sm text-gray-600">
        Remember your password? <router-link to="/login" class="font-medium text-primary-600 hover:text-primary-500">Sign in</router-link>
      </p>
    </div>

    <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
      <div class="bg-white py-8 px-4 shadow-lg sm:rounded-xl sm:px-10 border border-gray-100">
        <div v-if="submitted" class="text-center">
          <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-green-100 mb-4">
            <span class="text-2xl">&#x2709;</span>
          </div>
          <h3 class="text-lg font-semibold text-gray-900">Check your email</h3>
          <p class="mt-2 text-sm text-gray-600">If an account exists for {{ email }}, we've sent reset instructions.</p>
          <router-link to="/login" class="inline-block mt-6 px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-500">Back to sign in</router-link>
        </div>

        <template v-else>
          <div v-if="error" class="mb-6 rounded-lg bg-red-50 border border-red-200 p-4">
            <p class="text-sm text-red-700">{{ error }}</p>
          </div>
          <p class="mb-6 text-sm text-gray-600">Enter your email and we'll send you a link to reset your password.</p>
          <form @submit.prevent="handleSubmit" class="space-y-6">
            <div>
              <label for="email" class="block text-sm font-medium text-gray-700">Email address</label>
              <input id="email" v-model="email" type="email" autocomplete="email" required placeholder="you@example.com" class="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2.5 shadow-sm focus:ring-2 focus:ring-primary-600 focus:border-transparent outline-none sm:text-sm" />
            </div>
            <button type="submit" :disabled="loading" class="flex w-full justify-center rounded-lg bg-primary-600 px-3 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 disabled:opacity-50 transition-colors">
              {{ loading ? 'Sending...' : 'Send reset link' }}
            </button>
          </form>
        </template>
      </div>
    </div>
  </div>
</template>
