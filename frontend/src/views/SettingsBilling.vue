<script setup>
import { ref, onMounted } from 'vue'
import { getBilling } from '../composables/api.js'

const billing = ref(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    billing.value = await getBilling()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="max-w-2xl mx-auto">
    <h1 class="text-2xl font-bold text-gray-900 mb-6">Billing</h1>

    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
    </div>

    <div v-else-if="error" class="p-4 bg-red-50 border border-red-200 rounded-lg text-red-600">{{ error }}</div>

    <div v-else-if="billing" class="space-y-6">
      <div class="bg-white rounded-lg border p-6">
        <h2 class="text-lg font-semibold mb-4">Current Plan</h2>
        <div class="flex items-center justify-between">
          <div>
            <div class="text-2xl font-bold text-gray-900">{{ billing.plan }}</div>
            <div class="text-sm text-gray-500">{{ billing.price }}</div>
          </div>
          <button class="px-4 py-2 border rounded-lg text-sm hover:bg-gray-50">Change Plan</button>
        </div>
      </div>

      <div class="bg-white rounded-lg border p-6">
        <h2 class="text-lg font-semibold mb-4">Payment Method</h2>
        <div class="flex items-center justify-between">
          <span class="text-gray-700">{{ billing.payment_method }}</span>
          <button class="text-primary-600 hover:text-primary-800 text-sm">Update</button>
        </div>
        <div class="mt-2 text-sm text-gray-500">Next billing: {{ billing.next_billing }}</div>
      </div>

      <div class="bg-white rounded-lg border p-6">
        <h2 class="text-lg font-semibold mb-4">Invoices</h2>
        <div class="space-y-3">
          <div v-for="inv in billing.invoices" :key="inv.date" class="flex items-center justify-between py-2 border-b last:border-b-0">
            <span class="text-sm text-gray-700">{{ inv.date }}</span>
            <span class="text-sm font-medium">{{ inv.amount }}</span>
            <span class="px-2 py-0.5 rounded-full text-xs bg-green-100 text-green-700">{{ inv.status }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
