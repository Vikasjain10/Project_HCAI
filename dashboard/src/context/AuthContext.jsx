import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { fetchMe } from '../services/auth'
import { clearSession, getStoredUser, getToken, setSession } from '../services/authStorage'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = getToken()
    if (!token) {
      setUser(null)
      setLoading(false)
      return
    }

    const stored = getStoredUser()
    if (stored) setUser(stored)

    fetchMe()
      .then((profile) => {
        setUser(profile)
        const token = getToken()
        if (token) setSession(token, profile)
      })
      .catch(() => {
        clearSession()
        setUser(null)
      })
      .finally(() => setLoading(false))
  }, [])

  const value = useMemo(
    () => ({
      user,
      setUser,
      loading,
      isAuthenticated: Boolean(user),
      logout: () => {
        clearSession()
        setUser(null)
      },
    }),
    [user, loading],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
