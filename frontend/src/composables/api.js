const BASE = '/api'

async function request(path, options = {}) {
  const token = localStorage.getItem('teamflow_token')
  const headers = { 'Content-Type': 'application/json', ...options.headers }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${BASE}${path}`, { ...options, headers })

  if (res.status === 401) {
    localStorage.removeItem('teamflow_token')
    localStorage.removeItem('teamflow_user')
    window.location.href = '/login'
    throw new Error('Unauthorized')
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Request failed')
  }
  // Handle file downloads
  if (res.headers.get('content-type')?.includes('text/csv') || options.raw) {
    return res
  }
  return res.json()
}

// Auth
export const login = (email, password) => request('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) })
export const register = (email, name, password) => request('/auth/register', { method: 'POST', body: JSON.stringify({ email, name, password }) })
export const logout = () => request('/auth/logout', { method: 'POST' })
export const getMe = () => request('/auth/me')
export const forgotPassword = (email) => request('/auth/forgot-password', { method: 'POST', body: JSON.stringify({ email }) })

// Dashboard
export const getDashboard = () => request('/dashboard')

// Projects
export const getProjects = () => request('/projects')
export const getProject = (id) => request(`/projects/${id}`)
export const createProject = (data) => request('/projects', { method: 'POST', body: JSON.stringify(data) })
export const updateProject = (id, data) => request(`/projects/${id}`, { method: 'PUT', body: JSON.stringify(data) })
export const deleteProject = (id) => request(`/projects/${id}`, { method: 'DELETE' })

// Tasks
export const getTasks = (projectId, params = {}) => {
  const qs = new URLSearchParams()
  Object.entries(params).forEach(([k, v]) => { if (v !== undefined && v !== null && v !== '') qs.set(k, v) })
  return request(`/projects/${projectId}/tasks?${qs}`)
}
export const getTask = (taskId) => request(`/tasks/${taskId}`)
export const createTask = (projectId, data) => request(`/projects/${projectId}/tasks`, { method: 'POST', body: JSON.stringify(data) })
export const updateTask = (taskId, data) => request(`/tasks/${taskId}`, { method: 'PUT', body: JSON.stringify(data) })
export const deleteTask = (taskId) => request(`/tasks/${taskId}`, { method: 'DELETE' })

// Team
export const getMembers = (projectId) => request(`/projects/${projectId}/members`)
export const inviteMember = (projectId, email, role) => request(`/projects/${projectId}/members`, { method: 'POST', body: JSON.stringify({ email, role }) })
export const removeMember = (projectId, userId) => request(`/projects/${projectId}/members/${userId}`, { method: 'DELETE' })
export const updateMemberRole = (projectId, userId, role) => request(`/projects/${projectId}/members/${userId}/role`, { method: 'PUT', body: JSON.stringify({ role }) })

// Profile & Settings
export const updateProfile = (data) => request('/profile', { method: 'PUT', body: JSON.stringify(data) })
export const getBilling = () => request('/settings/billing')
export const getNotifications = () => request('/settings/notifications')
export const updateNotifications = (data) => request('/settings/notifications', { method: 'PUT', body: JSON.stringify(data) })

// Export
export const exportCSV = (projectId) => request(`/projects/${projectId}/export/csv`, { raw: true })
export const exportJSON = (projectId) => request(`/projects/${projectId}/export/json`, { raw: true })

// Users
export const getUsers = () => request('/users')

// Bugs
export const getBugs = () => request('/bugs')
export const getActiveBugs = () => request('/bugs/active')
export const toggleBug = (bugId) => request('/bugs/toggle', { method: 'POST', body: JSON.stringify({ bug_id: bugId }) })
export const applyPreset = (preset) => request('/bugs/preset', { method: 'POST', body: JSON.stringify({ preset }) })
export const getPresets = () => request('/bugs/presets')
