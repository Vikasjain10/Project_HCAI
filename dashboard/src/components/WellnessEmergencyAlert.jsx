import { Link } from 'react-router-dom'
import { WELLNESS_ALERT_THRESHOLD } from '../constants/brand'

export default function WellnessEmergencyAlert({ wellnessScore }) {
  if (wellnessScore == null) return null

  const score = Number(wellnessScore)
  if (score >= WELLNESS_ALERT_THRESHOLD) return null

  return (
    <div
      role="alert"
      className="animate-fade-in rounded-2xl border border-amber-300 bg-amber-50 p-4 dark:border-amber-600 dark:bg-amber-950/40"
    >
      <div className="flex items-start gap-3">
        <span className="text-xl" aria-hidden>
          ⚠️
        </span>
        <div>
          <h3 className="font-semibold text-amber-900 dark:text-amber-200">Wellness needs attention</h3>
          <p className="mt-1 text-sm text-amber-800 dark:text-amber-300">
            Your wellness score is {score}/100 (below {WELLNESS_ALERT_THRESHOLD}). Focus on sleep, recovery,
            and balanced activity. Consider speaking with a healthcare provider if you feel unwell.
          </p>
          <Link
            to="/"
            className="mt-2 inline-block text-xs font-medium text-amber-700 underline dark:text-amber-400"
          >
            Learn what wellness scores mean
          </Link>
        </div>
      </div>
    </div>
  )
}
