import api from './api'

export async function runFullAssessment(payload) {
  const { data } = await api.post('/full_assessment', payload)
  return data
}

export async function getRecommendations(payload) {
  const { data } = await api.post('/recommendation', payload)
  return data
}

export async function getExplanation(payload) {
  const { data } = await api.post('/explain', payload)
  return data
}
