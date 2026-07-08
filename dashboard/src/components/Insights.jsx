import { getRecommendations } from '../services/ai'
import AssessmentExplanations from './AssessmentExplanations'
import AiInsightResult from './AiInsightResult'

export default function Insights({
  healthInput,
  assessmentResult,
  recommendation,
  onRecommendation,
  loading,
  sessionData,
}) {
  const canGenerate = healthInput && assessmentResult

  const handleGenerate = async () => {
    if (!canGenerate) return
    await onRecommendation(() =>
      getRecommendations({
        ...healthInput,
        predictions: assessmentResult.predictions,
        wellness: assessmentResult.wellness,
      }),
    )
  }

  const comparison = sessionData?.comparison

  return (
    <div className="space-y-6">
      <div className="health-card">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-xl font-semibold">AI Health Insights</h2>
            <p className="text-sm text-slate-500">Grounded recommendations from your session history</p>
          </div>
          <button
            onClick={handleGenerate}
            disabled={!canGenerate || loading}
            className="rounded-full bg-slate-900 px-5 py-2.5 text-sm font-medium text-white transition hover:bg-slate-800 disabled:opacity-50"
          >
            {loading ? 'Generating...' : 'Generate Insights'}
          </button>
        </div>

        {!recommendation && (
          <p className="mt-4 rounded-2xl bg-slate-50 p-4 text-sm text-slate-500">
            Run an assessment on Overview, then generate personalized suggestions.
          </p>
        )}

        {recommendation && (
          <AiInsightResult
            recommendation={recommendation}
            wellnessScore={assessmentResult?.wellness?.score}
          />
        )}
      </div>

      {comparison && (
        <div className="health-card">
          <h3 className="mb-3 font-semibold">Session-Based Reasoning</h3>
          <p className="mb-4 text-sm text-slate-600">{comparison.summary}</p>
          <div className="grid gap-2 sm:grid-cols-2">
            {comparison.feature_changes?.map((change) => (
              <div key={change.feature} className="rounded-xl bg-slate-50 p-3 text-sm">
                <span className="font-medium">{change.label}</span>
                <p className="mt-1 text-slate-600">{change.message}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      <AssessmentExplanations
        explanations={assessmentResult?.explanations}
        explanation={recommendation?.explanation || assessmentResult?.explanation}
      />
    </div>
  )
}
