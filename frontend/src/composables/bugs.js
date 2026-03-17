import { ref } from 'vue'
import { getActiveBugs } from './api.js'

const activeBugs = ref(new Set())
let loaded = false

export async function loadBugs() {
  try {
    const data = await getActiveBugs()
    activeBugs.value = new Set(data.active || [])
    loaded = true
  } catch {
    activeBugs.value = new Set()
  }
}

export function isBugActive(bugId) {
  return activeBugs.value.has(bugId)
}

export function useBugs() {
  if (!loaded) loadBugs()
  return { activeBugs, isBugActive, loadBugs }
}
