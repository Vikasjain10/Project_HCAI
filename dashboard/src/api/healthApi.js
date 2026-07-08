import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
})

export const DEFAULT_HEALTH_INPUT = {
  avg_hr: 72,
  rhr: 58,
  sleep_duration_h: 7.5,
  deep_sleep_in_minutes: 90,
  steps: 8500,
  exercise_duration: 45,
  stress: 35,
  readiness: 75,
}

export async function runFullAssessment(data) {
  const response = await api.post('/full_assessment', data)
  return response.data
}

export async function getRecommendations(data) {
  const response = await api.post('/recommendation', data)
  return response.data
}

export async function fetchPredictionHistory() {
  const response = await api.get('/history/predictions')
  return response.data.items
}

export async function deletePrediction(id) {
  await api.delete(`/history/predictions/${id}`)
}

export async function fetchAnalytics() {
  const response = await api.get('/analytics')
  return response.data
}

export default api
