import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { DEFAULT_HEALTH_INPUT, fetchDashboardSummary, fetchSessionHistory } from '../services/data'
import { runFullAssessment } from '../services/ai'

const DashboardContext = createContext(null)

export function DashboardProvider({ children }) {
  const [healthInput, setHealthInput] = useState(DEFAULT_HEALTH_INPUT)
  const [summary, setSummary] = useState(null)
  const [sessionData, setSessionData] = useState(null)
  const [assessmentResult, setAssessmentResult] = useState(null)
  const [recommendation, setRecommendation] = useState(null)
  const [loading, setLoading] = useState({
    summary: true,
    sessions: true,
    assessment: false,
    recommendation: false,
  })
  const [errors, setErrors] = useState({})

  const refresh = useCallback(async () => {
    setLoading((l) => ({ ...l, summary: true, sessions: true }))
    try {
      const [s, sessions] = await Promise.all([fetchDashboardSummary(), fetchSessionHistory(14)])
      setSummary(s)
      setSessionData(sessions)
    } catch {
      setSummary(null)
      setSessionData(null)
    } finally {
      setLoading((l) => ({ ...l, summary: false, sessions: false }))
    }
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  const handleChange = (key, value) => setHealthInput((p) => ({ ...p, [key]: value }))

  const runAssessment = async () => {
    setLoading((l) => ({ ...l, assessment: true }))
    setErrors({})
    setRecommendation(null)
    try {
      const result = await runFullAssessment(healthInput)
      setAssessmentResult(result)
      setSummary((prev) => ({
        ...prev,
        sleep_hours: healthInput.sleep_duration_h,
        activity_steps: healthInput.steps,
        stress_score: healthInput.stress,
        health_status: result.predictions?.stress ?? prev?.health_status,
        wellness_score: result.wellness?.score ?? prev?.wellness_score,
        risk_score: result.risk_score ?? prev?.risk_score,
        session_count: (prev?.session_count ?? 0) + 1,
        last_updated: new Date().toISOString(),
      }))
      setSessionData((prev) =>
        prev?.has_data
          ? { ...prev, session_count: (prev.session_count ?? 0) + 1 }
          : prev,
      )
      await refresh()
    } catch (err) {
      setErrors({ general: err.response?.data?.detail || 'Assessment failed' })
    } finally {
      setLoading((l) => ({ ...l, assessment: false }))
    }
  }

  const generateRecommendation = async (fetcher) => {
    setLoading((l) => ({ ...l, recommendation: true }))
    try {
      const result = await fetcher()
      setRecommendation(result)
    } catch (err) {
      setErrors({ general: err.response?.data?.detail || 'Failed to generate insights' })
    } finally {
      setLoading((l) => ({ ...l, recommendation: false }))
    }
  }

  return (
    <DashboardContext.Provider
      value={{
        healthInput,
        handleChange,
        summary,
        sessionData,
        assessmentResult,
        recommendation,
        loading,
        errors,
        runAssessment,
        generateRecommendation,
        refresh,
      }}
    >
      {children}
    </DashboardContext.Provider>
  )
}

export function useDashboard() {
  const ctx = useContext(DashboardContext)
  if (!ctx) throw new Error('useDashboard must be used within DashboardProvider')
  return ctx
}
