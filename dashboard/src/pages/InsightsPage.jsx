import Insights from '../components/Insights'
import { useDashboard } from '../context/DashboardContext'

export default function InsightsPage() {
  const {
    healthInput,
    assessmentResult,
    recommendation,
    sessionData,
    loading,
    generateRecommendation,
  } = useDashboard()

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h2 className="text-2xl font-bold">Insights</h2>
        <p className="text-slate-500">AI recommendations grounded in your metrics and sessions</p>
      </div>
      <Insights
        healthInput={healthInput}
        assessmentResult={assessmentResult}
        recommendation={recommendation}
        onRecommendation={generateRecommendation}
        loading={loading.recommendation}
        sessionData={sessionData}
      />
    </div>
  )
}
