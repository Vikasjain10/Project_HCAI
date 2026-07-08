import api from './api'

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

export async function fetchDashboardSummary() {
  const { data } = await api.get('/dashboard/summary')
  return data
}

export async function fetchSessionHistory(limit = 14) {
  const { data } = await api.get('/sessions/history', { params: { limit } })
  return data
}

export async function fetchAnalytics() {
  const { data } = await api.get('/analytics')
  return data
}

export async function fetchPredictionHistory() {
  const { data } = await api.get('/history/predictions')
  return data.items
}

export async function deletePrediction(id) {
  await api.delete(`/history/predictions/${id}`)
}

export async function fetchRecommendations() {
  const { data } = await api.get('/history/recommendations')
  return data.items
}
