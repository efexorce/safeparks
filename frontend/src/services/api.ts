import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const cameraApi = {
  list: (params?: Record<string, unknown>) => api.get('/cameras/', { params }),
  get: (id: string) => api.get(`/cameras/${id}`),
  create: (data: unknown) => api.post('/cameras/', data),
  update: (id: string, data: unknown) => api.put(`/cameras/${id}`, data),
  delete: (id: string) => api.delete(`/cameras/${id}`),
  mapData: () => api.get('/cameras/map'),
  stats: () => api.get('/cameras/stats'),
  bandwidth: (id: string) => api.get(`/cameras/${id}/bandwidth`),
}

export const alarmApi = {
  list: (params?: Record<string, unknown>) => api.get('/alarms/', { params }),
  get: (id: string) => api.get(`/alarms/${id}`),
  summary: () => api.get('/alarms/summary'),
  acknowledge: (id: string, userId: string) =>
    api.post(`/alarms/${id}/acknowledge`, { user_id: userId }),
  resolve: (id: string, userId: string, notes?: string) =>
    api.post(`/alarms/${id}/resolve`, { user_id: userId, notes }),
  markFalsePositive: (id: string, userId: string, reason: string) =>
    api.post(`/alarms/${id}/false-positive`, { user_id: userId, reason }),
}

export const energyApi = {
  cityStats: () => api.get('/energy/city-stats'),
  solarPanels: () => api.get('/energy/solar-panels'),
  cameraHistory: (id: string, params?: Record<string, unknown>) =>
    api.get(`/energy/cameras/${id}/history`, { params }),
}

export const reportApi = {
  daily: (date?: string) => api.get('/reports/daily', { params: { date } }),
  monthly: (year: number, month: number) =>
    api.get('/reports/monthly', { params: { year, month } }),
}

export const authApi = {
  login: (username: string, password: string) =>
    api.post('/auth/login', { username, password }),
  register: (data: unknown) => api.post('/auth/register', data),
}

export default api
