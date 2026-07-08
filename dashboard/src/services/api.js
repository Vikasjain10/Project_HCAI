import axios from 'axios'
import { getToken, clearSession } from './authStorage'

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
})

api.interceptors.request.use((config) => {
  const token = getToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const path = err.config?.url || ''
    if (err.response?.status === 401 && !path.includes('/auth/login') && !path.includes('/auth/signup')) {
      clearSession()
    }
    return Promise.reject(err)
  },
)

export default api
