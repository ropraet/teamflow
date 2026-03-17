<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { createProject } from '../composables/api.js'
import { isBugActive } from '../composables/bugs.js'

const router = useRouter()
const step = ref(1)
const submitting = ref(false)
const error = ref('')

// Form data
const title = ref('')
const description = ref('')
const color = ref('#3B82F6')

const colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16']

// BUG: wizard_wrong_step_indicator — shows wrong step
const displayStep = computed(() => {
  if (isBugActive('wizard_wrong_step_indicator') && step.value === 3) return 2
  return step.value
})

function nextStep() {
  if (step.value === 1 && !title.value.trim()) {
    error.value = 'Please enter a project title'
    return
  }
  error.value = ''
  step.value++
}

function prevStep() {
  error.value = ''
  if (isBugActive('wizard_back_loses_data')) {
    // BUG: wizard_back_loses_data — clear data when going back
    if (step.value === 2) title.value = ''
    if (step.value === 3) description.value = ''
  }
  step.value--
}

async function submit() {
  submitting.value = true
  error.value = ''
  try {
    const project = await createProject({ title: title.value, description: description.value, color: color.value })
    router.push(`/projects/${project.id}`)
  } catch (e) {
    error.value = e.message
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="max-w-2xl mx-auto">
    <h1 class="text-2xl font-bold text-gray-900 mb-6">Create New Project</h1>

    <!-- Step indicator -->
    <div class="flex items-center gap-2 mb-8">
      <div v-for="s in 3" :key="s" class="flex items-center gap-2">
        <div
          class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium"
          :class="s <= displayStep ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-500'"
        >{{ s }}</div>
        <span class="text-sm" :class="s <= displayStep ? 'text-primary-600 font-medium' : 'text-gray-400'">
          {{ s === 1 ? 'Basics' : s === 2 ? 'Details' : 'Review' }}
        </span>
        <div v-if="s < 3" class="w-12 h-0.5" :class="s < displayStep ? 'bg-primary-600' : 'bg-gray-200'"></div>
      </div>
    </div>

    <div class="bg-white rounded-lg border p-6">
      <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">{{ error }}</div>

      <!-- Step 1: Basics -->
      <div v-if="step === 1">
        <h2 class="text-lg font-semibold mb-4">Project Basics</h2>
        <div class="space-y-4">
          <div>
            <!-- BUG: a11y_missing_form_labels — no label when bug active -->
            <label v-if="!isBugActive('a11y_missing_form_labels')" for="title" class="block text-sm font-medium text-gray-700 mb-1">Project Title</label>
            <input
              id="title"
              v-model="title"
              type="text"
              :placeholder="isBugActive('a11y_missing_form_labels') ? 'Project Title' : 'Enter project title'"
              class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Color</label>
            <div class="flex gap-2">
              <button
                v-for="c in colors"
                :key="c"
                @click="color = c"
                class="w-8 h-8 rounded-full border-2 transition-all"
                :class="color === c ? 'border-gray-900 scale-110' : 'border-transparent'"
                :style="{ backgroundColor: c }"
              ></button>
            </div>
          </div>
        </div>
      </div>

      <!-- Step 2: Details -->
      <div v-if="step === 2">
        <h2 class="text-lg font-semibold mb-4">Project Details</h2>
        <div>
          <label v-if="!isBugActive('a11y_missing_form_labels')" for="description" class="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <textarea
            id="description"
            v-model="description"
            rows="5"
            :placeholder="isBugActive('a11y_missing_form_labels') ? 'Description' : 'Describe your project...'"
            class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none resize-none"
          ></textarea>
        </div>
      </div>

      <!-- Step 3: Review -->
      <div v-if="step === 3">
        <h2 class="text-lg font-semibold mb-4">Review & Create</h2>
        <div class="space-y-3">
          <div class="flex items-center gap-3">
            <div class="w-4 h-4 rounded-full" :style="{ backgroundColor: color }"></div>
            <span class="font-medium">{{ title || '(no title)' }}</span>
          </div>
          <p class="text-sm text-gray-600">{{ description || '(no description)' }}</p>
        </div>
      </div>

      <!-- Navigation -->
      <div class="flex justify-between mt-6 pt-4 border-t">
        <button v-if="step > 1" @click="prevStep" class="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 border rounded-lg hover:bg-gray-50">
          Back
        </button>
        <div v-else></div>
        <button
          v-if="step < 3"
          @click="nextStep"
          class="px-6 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700"
        >
          Next
        </button>
        <button
          v-else
          @click="submit"
          :disabled="submitting"
          class="px-6 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 disabled:opacity-50"
        >
          {{ submitting ? 'Creating...' : 'Create Project' }}
        </button>
      </div>
    </div>
  </div>
</template>
