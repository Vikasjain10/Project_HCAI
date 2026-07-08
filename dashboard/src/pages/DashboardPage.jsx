import { useCallback, useEffect, useState } from 'react'
import {
  DEFAULT_HEALTH_INPUT,
  fetchAnalytics,
  fetchPredictionHistory,
  runFullAssessment,
} from '../api/healthApi'
import AIAdvisor from '../components/AIAdvisor'
import AnalyticsCharts from '../components/AnalyticsCharts'
import HealthInputForm from '../components/HealthInputForm'
import PredictionsCard from '../components/PredictionsCard'
import WellnessGauge from '../components/WellnessGauge'

const FIELD_LIMITS = {
  avg_hr: [40, 200],
  rhr: [30, 120],
  sleep_duration_h: [0, 16],
  deep_sleep_in_minutes: [0, 300],
  steps: [0, 50000],
  exercise_duration: [0, 300],
  stress: [0, 100],
  readiness: [0, 100],
}

function validateInput(values) {
  const errors = {}
  Object.entries(FIELD_LIMITS).forEach(([key, [min, max]]) => {
    const val = values[key]
    if (val < min || val > max || Number.isNaN(val)) {
      errors[key] = `Must be between ${min} and ${max}`
    }
  })
  return errors
}

export default function DashboardPage() {
  const [healthInput, setHealthInput] = useState(DEFAULT_HEALTH_INPUT)
  const [errors, setErrors] = useState({})
  const [assessmentLoading, setAssessmentLoading] = useState(false)
  const [recommendationLoading, setRecommendationLoading] = useState(false)
  const [assessmentResult, setAssessmentResult] = useState(null)
  const [recommendation, setRecommendation] = useState(null)
  const [analytics, setAnalytics] = useState(null)
  const [analyticsLoading, setAnalyticsLoading] = useState(true)

  const loadAnalytics = useCallback(async () => {
    setAnalyticsLoading(true)
    try {
      const data = await fetchAnalytics()
      setAnalytics(data)
    } catch {
      setAnalytics(null)
    } finally {
      setAnalyticsLoading(false)
    }
  }, [])

  useEffect(() => {
    loadAnalytics()
  }, [loadAnalytics])

  const handleChange = (key, value) => {
    setHealthInput((prev) => ({ ...prev, [key]: value }))
  }

  const handleAssessment = async () => {
    const validationErrors = validateInput(healthInput)
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors)
      return
    }
    setErrors({})
    setAssessmentLoading(true)
    setRecommendation(null)
    try {
      const result = await runFullAssessment(healthInput)
      setAssessmentResult(result)
      await loadAnalytics()
    } catch (err) {
      setErrors({ general: err.response?.data?.detail || 'Assessment failed. Is the backend running?' })
    } finally {
      setAssessmentLoading(false)
    }
  }

  const handleRecommendation = async (fetcher) => {
    setRecommendationLoading(true)
    try {
      const result = await fetcher()
      setRecommendation(result)
    } catch (err) {
      setErrors({ general: err.response?.data?.detail || 'Failed to generate recommendations.' })
    } finally {
      setRecommendationLoading(false)
    }
  }

  return (
    <div className="space-y-8">
      <section className="grid gap-6 xl:grid-cols-3">
        <div className="xl:col-span-2">
          <HealthInputForm
            values={healthInput}
            onChange={handleChange}
            onSubmit={handleAssessment}
            loading={assessmentLoading}
            errors={errors}
          />
        </div>
        <div className="grid gap-6">
          <PredictionsCard predictions={assessmentResult?.predictions} />
          <WellnessGauge score={assessmentResult?.wellness?.score} />
        </div>
      </section>

      <section>
        <h2 className="mb-4 text-lg font-semibold">Analytics Dashboard</h2>
        <AnalyticsCharts analytics={analytics} loading={analyticsLoading} />
      </section>

      <section>
        <AIAdvisor
          healthInput={healthInput}
          assessmentResult={assessmentResult}
          recommendation={recommendation}
          onRecommendation={handleRecommendation}
          loading={recommendationLoading}
        />
      </section>
    </div>
  )
}
