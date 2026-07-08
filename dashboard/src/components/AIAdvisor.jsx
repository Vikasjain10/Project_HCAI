import { getRecommendations } from '../api/healthApi'
import { getRiskColor } from '../utils/colors'

export default function AIAdvisor({ healthInput, assessmentResult, recommendation, onRecommendation, loading }) {
  const canGenerate = healthInput && assessmentResult

  const handleGenerate = async () => {
    if (!canGenerate) return
    const payload = {
      ...healthInput,
      predictions: assessmentResult.predictions,
      wellness: assessmentResult.wellness,
    }
    await onRecommendation(() => getRecommendations(payload))
  }

  return (
    <div className="card">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-semibold">AI Health Advisor</h2>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Personalized lifestyle and wellness suggestions
          </p>
        </div>
        <button
          onClick={handleGenerate}
          disabled={!canGenerate || loading}
          className="rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? 'Generating...' : 'Generate Recommendations'}
        </button>
      </div>

      {!recommendation && (
        <p className="rounded-xl bg-slate-50 p-4 text-sm text-slate-500 dark:bg-slate-800/60 dark:text-slate-400">
          Run an assessment first, then generate AI-powered wellness advice.
        </p>
      )}

      {recommendation && (
        <div className="space-y-4">
          <div className="flex items-start justify-between gap-4">
            <p className="text-slate-700 dark:text-slate-200">{recommendation.summary}</p>
            <span className={`shrink-0 rounded-full border px-3 py-1 text-xs font-semibold ${getRiskColor(recommendation.risk_level)}`}>
              {recommendation.risk_level} Risk
            </span>
          </div>

          {recommendation.reasoning && (
            <div className="rounded-2xl bg-indigo-50 p-4 text-sm text-indigo-900 dark:bg-indigo-950/40 dark:text-indigo-100">
              <p className="font-medium">Why these suggestions?</p>
              <p className="mt-1">{recommendation.reasoning}</p>
            </div>
          )}

          <div>
            <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-500">Key Issues</h3>
            <ul className="list-inside list-disc space-y-1 text-sm text-slate-700 dark:text-slate-300">
              {recommendation.key_issues?.map((issue) => (
                <li key={issue}>{issue}</li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-500">Recommendations</h3>
            <ul className="list-inside list-disc space-y-1 text-sm text-slate-700 dark:text-slate-300">
              {recommendation.recommendations?.map((rec) => (
                <li key={rec}>{rec}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}
