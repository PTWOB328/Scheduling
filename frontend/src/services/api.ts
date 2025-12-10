import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add token to requests
export const authService = {
  setToken: (token: string | null) => {
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
    } else {
      delete api.defaults.headers.common['Authorization']
    }
  },
  login: async (username: string, password: string) => {
    const formData = new URLSearchParams()
    formData.append('username', username)
    formData.append('password', password)
    const response = await api.post('/api/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    return response.data
  },
  getCurrentUser: async () => {
    const response = await api.get('/api/auth/me')
    return response.data
  },
}

export const pilotService = {
  getAll: () => api.get('/api/pilots/'),
  getById: (id: number) => api.get(`/api/pilots/${id}`),
  create: (data: any) => api.post('/api/pilots/', data),
  update: (id: number, data: any) => api.put(`/api/pilots/${id}`, data),
  delete: (id: number) => api.delete(`/api/pilots/${id}`),
}

export const eventService = {
  getAll: (params?: any) => api.get('/api/events/', { params }),
  getById: (id: number) => api.get(`/api/events/${id}`),
  create: (data: any) => api.post('/api/events/', data),
  update: (id: number, data: any) => api.put(`/api/events/${id}`, data),
  delete: (id: number) => api.delete(`/api/events/${id}`),
  updateStatus: (id: number, status: string) =>
    api.patch(`/api/events/${id}/status`, null, { params: { new_status: status } }),
}

export const currencyService = {
  import: (file: File, fileType: string) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('file_type', fileType)
    return api.post('/api/currency/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  getByPilot: (pilotId: number) => api.get(`/api/currency/pilot/${pilotId}`),
}

export const trainingService = {
  getRequirements: () => api.get('/api/training/requirements'),
  createRequirement: (data: any) => api.post('/api/training/requirements', data),
  getPilotStatus: (pilotId: number, evaluationMonth: string) =>
    api.get(`/api/training/status/pilot/${pilotId}`, {
      params: { evaluation_month: evaluationMonth },
    }),
  evaluatePilot: (pilotId: number, evaluationMonth: string) =>
    api.post(`/api/training/status/evaluate/${pilotId}`, null, {
      params: { evaluation_month: evaluationMonth },
    }),
  evaluateAll: (evaluationMonth: string) =>
    api.post('/api/training/status/evaluate-all', null, {
      params: { evaluation_month: evaluationMonth },
    }),
}

export const schedulerService = {
  optimize: (eventIds: number[], constraints: any) =>
    api.post('/api/scheduler/optimize', {
      event_ids: eventIds,
      constraints: constraints || {},
    }),
  suggest: (startDate: string, endDate: string, eventType: string, constraints: any) =>
    api.post('/api/scheduler/suggest', {
      start_date: startDate,
      end_date: endDate,
      event_type: eventType,
      constraints: constraints || {},
    }),
}

export const calendarService = {
  getPilotCalendar: (pilotId: number, startDate?: string, endDate?: string) =>
    api.get(`/api/calendar/pilot/${pilotId}/ics`, {
      params: { start_date: startDate, end_date: endDate },
      responseType: 'blob',
    }),
  getPilotCalendarUrl: (pilotId: number) =>
    api.get(`/api/calendar/pilot/${pilotId}/calendar-url`),
}

export default api
