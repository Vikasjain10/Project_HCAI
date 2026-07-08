import HealthInputForm from '../components/HealthInputForm'
import AiInsightResult from '../components/AiInsightResult'
import AssessmentExplanations from '../components/AssessmentExplanations'
import PredictionsCard from '../components/PredictionsCard'
import UserSummary from '../components/UserSummary'
import WellnessEmergencyAlert from '../components/WellnessEmergencyAlert'
import { useDashboard } from '../context/DashboardContext'
import { getRecommendations } from '../services/ai'

export default function OverviewPage() {
  const {
    healthInput,
    handleChange,
    summary,
    assessmentResult,
    recommendation,
    loading,
    errors,
    runAssessment,
    generateRecommendation,
  } = useDashboard()

  const canGenerateInsights = healthInput && assessmentResult
  const wellnessScore = assessmentResult?.wellness?.score ?? summary?.wellness_score ?? null

  const handleGenerateInsights = async () => {
    if (!canGenerateInsights) return
    await generateRecommendation(() =>
      getRecommendations({
        ...healthInput,
        predictions: assessmentResult.predictions,
        wellness: assessmentResult.wellness,
      }),
    )
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="relative overflow-hidden rounded-3xl border border-sky-100 bg-gradient-to-br from-sky-50 via-white to-indigo-50 p-8 dark:border-sky-900 dark:from-slate-900 dark:via-slate-900 dark:to-indigo-950/40">
        <div className="flex flex-wrap items-center gap-6">
          <div className="flex h-20 w-20 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-sky-500 to-indigo-600 text-4xl text-white shadow-lg shadow-sky-500/30">
            ▶
          </div>
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Run your assessment</h2>
            <p className="mt-1 text-slate-600 dark:text-slate-400">
              Enter today&apos;s wearable metrics to predict stress, fatigue, and your wellness score.
            </p>
          </div>
        </div>
      </div>

      <WellnessEmergencyAlert wellnessScore={wellnessScore} />

      <UserSummary summary={summary} loading={loading.summary} />

      <div className="grid gap-6 xl:grid-cols-3">
        <div className="xl:col-span-2">
          <HealthInputForm
            values={healthInput}
            onChange={handleChange}
            onSubmit={runAssessment}
            loading={loading.assessment}
            errors={errors}
          />
        </div>
        <div>
          <PredictionsCard
            predictions={assessmentResult?.predictions}
            stressFeatures={assessmentResult?.stress_features}
            fatigueFeatures={assessmentResult?.fatigue_features}
            wellnessBreakdown={assessmentResult?.wellness?.breakdown}
            wellnessScore={wellnessScore}
          />
        </div>
      </div>

      <AssessmentExplanations
        explanations={assessmentResult?.explanations}
        explanation={assessmentResult?.explanation}
      />

      <div className="health-card">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white">AI Wellness Reasoning</h3>
            <p className="text-sm text-slate-500">Suggestions grounded in your session history</p>
          </div>
          <button
            type="button"
            onClick={handleGenerateInsights}
            disabled={!canGenerateInsights || loading.recommendation}
            className="rounded-full bg-indigo-600 px-5 py-2.5 text-sm font-medium text-white transition hover:bg-indigo-500 disabled:opacity-50"
          >
            {loading.recommendation ? 'Reasoning...' : 'Generate AI Insights'}
          </button>
        </div>

        {!recommendation && (
          <p className="mt-4 rounded-2xl bg-slate-50 p-4 text-sm text-slate-500 dark:bg-slate-800 dark:text-slate-400">
            Run an assessment above, then generate AI reasoning.
          </p>
        )}

        <AiInsightResult recommendation={recommendation} wellnessScore={wellnessScore} />
      </div>
    </div>
  )
}
