import { getRiskColor } from '../utils/colors'
import { WELLNESS_POSITIVE_THRESHOLD } from '../constants/brand'

export default function AiInsightResult({ recommendation, wellnessScore }) {
  if (!recommendation) return null

  const score = wellnessScore != null ? Number(wellnessScore) : null
  const isPositive =
    recommendation.is_positive === true ||
    (score != null && score > WELLNESS_POSITIVE_THRESHOLD && recommendation.risk_level === 'Low')

  return (
    <div className="mt-4 space-y-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="space-y-1">
          <p className={`text-slate-700 dark:text-slate-300 ${isPositive ? 'text-emerald-800 dark:text-emerald-200' : ''}`}>
            {recommendation.summary}
          </p>
          {recommendation.llm_source && (
            <p className="text-xs text-slate-400 dark:text-slate-500">
              {recommendation.llm_source === 'rule-based-fallback'
                ? 'Source: Built-in rules (LLM unavailable)'
                : recommendation.llm_source.startsWith('openrouter:')
                  ? `Source: OpenRouter · ${recommendation.llm_source.replace('openrouter:', '')}`
                  : `Source: ${recommendation.llm_source}`}
            </p>
          )}
        </div>
        <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${getRiskColor(recommendation.risk_level)}`}>
          {recommendation.risk_level} Risk
        </span>
      </div>

      {isPositive && (
        <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-900 dark:border-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-200">
          <p className="font-medium">Great job — keep it up!</p>
          <p className="mt-1">
            Your overall wellness is in a healthy range. Stay hydrated, maintain balanced activity, and
            continue a low-stress, low-fatigue lifestyle.
          </p>
        </div>
      )}

      {recommendation.reasoning && (
        <div
          className={`rounded-2xl p-4 text-sm ${
            isPositive
              ? 'bg-emerald-50/80 text-emerald-900 dark:bg-emerald-950/30 dark:text-emerald-200'
              : 'bg-indigo-50 text-indigo-900 dark:bg-indigo-950/50 dark:text-indigo-200'
          }`}
        >
          <p className="font-medium">Why these suggestions?</p>
          <p className="mt-1">{recommendation.reasoning}</p>
        </div>
      )}

      {(recommendation.stress_explanation ||
        recommendation.fatigue_explanation ||
        recommendation.wellness_explanation) && (
        <div className="grid gap-3 md:grid-cols-3">
          {recommendation.stress_explanation && (
            <div className="rounded-2xl border border-rose-100 bg-rose-50/60 p-4 text-sm dark:border-rose-900/40 dark:bg-rose-950/30">
              <p className="font-semibold text-rose-800 dark:text-rose-200">Stress</p>
              <p className="mt-1 text-slate-700 dark:text-slate-300">{recommendation.stress_explanation}</p>
            </div>
          )}
          {recommendation.fatigue_explanation && (
            <div className="rounded-2xl border border-orange-100 bg-orange-50/60 p-4 text-sm dark:border-orange-900/40 dark:bg-orange-950/30">
              <p className="font-semibold text-orange-800 dark:text-orange-200">Fatigue</p>
              <p className="mt-1 text-slate-700 dark:text-slate-300">{recommendation.fatigue_explanation}</p>
            </div>
          )}
          {recommendation.wellness_explanation && (
            <div className="rounded-2xl border border-emerald-100 bg-emerald-50/60 p-4 text-sm dark:border-emerald-900/40 dark:bg-emerald-950/30">
              <p className="font-semibold text-emerald-800 dark:text-emerald-200">Wellness</p>
              <p className="mt-1 text-slate-700 dark:text-slate-300">{recommendation.wellness_explanation}</p>
            </div>
          )}
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <h4 className="mb-2 text-sm font-semibold text-slate-600 dark:text-slate-400">
            {isPositive ? 'Highlights' : 'Key issues'}
          </h4>
          <ul className="space-y-1 text-sm text-slate-700 dark:text-slate-300">
            {recommendation.key_issues?.map((item) => (
              <li key={item} className="flex gap-2">
                <span className={isPositive ? 'text-emerald-500' : 'text-red-400'}>•</span> {item}
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h4 className="mb-2 text-sm font-semibold text-slate-600 dark:text-slate-400">Recommendations</h4>
          <ul className="space-y-1 text-sm text-slate-700 dark:text-slate-300">
            {recommendation.recommendations?.map((item) => (
              <li key={item} className="flex gap-2">
                <span className="text-emerald-500">•</span> {item}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {(recommendation.daily_suggestions?.length > 0 ||
        recommendation.weekly_suggestions?.length > 0) && (
        <div className="grid gap-4 md:grid-cols-2">
          {recommendation.daily_suggestions?.length > 0 && (
            <div className="rounded-2xl bg-slate-50 p-4 dark:bg-slate-800/60">
              <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-200">Today</h4>
              <ul className="mt-2 space-y-1 text-sm text-slate-600 dark:text-slate-300">
                {recommendation.daily_suggestions.map((item) => (
                  <li key={item}>• {item}</li>
                ))}
              </ul>
            </div>
          )}
          {recommendation.weekly_suggestions?.length > 0 && (
            <div className="rounded-2xl bg-slate-50 p-4 dark:bg-slate-800/60">
              <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-200">This week</h4>
              <ul className="mt-2 space-y-1 text-sm text-slate-600 dark:text-slate-300">
                {recommendation.weekly_suggestions.map((item) => (
                  <li key={item}>• {item}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
