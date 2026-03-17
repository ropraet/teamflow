<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getMembers, inviteMember, removeMember, updateMemberRole } from '../composables/api.js'

const props = defineProps({ id: [String, Number] })
const router = useRouter()
const members = ref([])
const loading = ref(true)
const inviteEmail = ref('')
const inviteRole = ref('member')
const inviting = ref(false)
const message = ref('')
const error = ref('')

async function load() {
  loading.value = true
  try {
    members.value = await getMembers(props.id)
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function handleInvite() {
  if (!inviteEmail.value) return
  inviting.value = true
  error.value = ''
  message.value = ''
  try {
    const result = await inviteMember(props.id, inviteEmail.value, inviteRole.value)
    message.value = result.message || 'Invited!'
    inviteEmail.value = ''
    // Reload to check if member was actually added
    await load()
  } catch (e) {
    error.value = e.message
  } finally {
    inviting.value = false
  }
}

async function handleRemove(userId) {
  if (!confirm('Remove this member?')) return
  try {
    await removeMember(props.id, userId)
    members.value = members.value.filter(m => m.user_id !== userId)
  } catch (e) {
    alert(e.message)
  }
}

async function handleRoleChange(userId, role) {
  try {
    await updateMemberRole(props.id, userId, role)
  } catch (e) {
    alert(e.message)
  }
}

onMounted(load)
</script>

<template>
  <div class="max-w-3xl mx-auto">
    <div class="flex items-center gap-3 mb-6">
      <button @click="router.push(`/projects/${id}`)" class="text-gray-400 hover:text-gray-600">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
      </button>
      <h1 class="text-2xl font-bold text-gray-900">Team Members</h1>
    </div>

    <!-- Invite form -->
    <div class="bg-white rounded-lg border p-5 mb-6">
      <h2 class="text-lg font-semibold mb-3">Invite Member</h2>
      <div v-if="message" class="mb-3 p-3 bg-green-50 border border-green-200 rounded-lg text-sm text-green-600">{{ message }}</div>
      <div v-if="error" class="mb-3 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">{{ error }}</div>
      <div class="flex gap-3">
        <input
          v-model="inviteEmail"
          type="email"
          placeholder="Email address"
          class="flex-1 px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 outline-none text-sm"
        />
        <select v-model="inviteRole" class="px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-primary-500 outline-none">
          <option value="member">Member</option>
          <option value="admin">Admin</option>
        </select>
        <button
          @click="handleInvite"
          :disabled="inviting"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 disabled:opacity-50"
        >
          {{ inviting ? 'Inviting...' : 'Invite' }}
        </button>
      </div>
    </div>

    <!-- Members list -->
    <div class="bg-white rounded-lg border">
      <div v-if="loading" class="flex items-center justify-center py-10">
        <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
      </div>
      <div v-else>
        <div v-for="m in members" :key="m.id" class="flex items-center justify-between p-4 border-b last:border-b-0">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-primary-100 text-primary-600 flex items-center justify-center font-medium">
              {{ m.name?.[0] || '?' }}
            </div>
            <div>
              <div class="font-medium text-gray-900">{{ m.name }}</div>
              <div class="text-sm text-gray-500">{{ m.email }}</div>
            </div>
          </div>
          <div class="flex items-center gap-3">
            <select
              :value="m.role"
              @change="handleRoleChange(m.user_id, $event.target.value)"
              class="px-2 py-1 border rounded text-sm focus:ring-2 focus:ring-primary-500 outline-none"
            >
              <option value="member">Member</option>
              <option value="admin">Admin</option>
            </select>
            <button @click="handleRemove(m.user_id)" class="text-red-500 hover:text-red-700 text-sm">Remove</button>
          </div>
        </div>
      </div>
      <div v-if="!loading && members.length === 0" class="text-center py-10 text-gray-400">No team members yet</div>
    </div>
  </div>
</template>
