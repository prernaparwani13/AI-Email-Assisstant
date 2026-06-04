import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle 401 globally
api.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// ── Auth ─────────────────────────────────────────────────────────────
export const authApi = {
  getLoginUrl: () => api.get('/auth/login'),
  getMe: () => api.get('/auth/me'),
}

// ── Emails ───────────────────────────────────────────────────────────
export const emailApi = {
  getInbox: (params = {}) => api.get('/emails', { params }),
  getEmail: (id) => api.get(`/emails/${id}`),
  markRead: (id) => api.post(`/emails/${id}/read`),
  deleteEmail: (id) => api.delete(`/emails/${id}`),
  sendEmail: (data) => api.post('/emails/send', data),
  searchEmails: (q, max_results = 20) =>
    api.get('/emails/search/query', { params: { q, max_results } }),
}

// ── AI ───────────────────────────────────────────────────────────────
export const aiApi = {
  generateReply: (data) => api.post('/ai/reply', data),
  summarize: (data) => api.post('/ai/summarize', data),
  correctGrammar: (data) => api.post('/ai/grammar', data),
  classify: (data) => api.post('/ai/classify', data),
  compose: (prompt, tone = 'professional') =>
    api.post('/ai/compose', null, { params: { prompt, tone } }),
}

export default api
