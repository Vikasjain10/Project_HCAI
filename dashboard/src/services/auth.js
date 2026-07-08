import api from './api'
import { setSession } from './authStorage'

export async function signup(payload) {
  const { data } = await api.post('/auth/signup', payload)
  return data
}

export async function login(email, password) {
  const { data } = await api.post('/auth/login', { email, password })
  setSession(data.token, data.user)
  return data
}

export async function fetchMe() {
  const { data } = await api.get('/auth/me')
  return data
}
