import SessionTrends from '../components/SessionTrends'
import { useDashboard } from '../context/DashboardContext'

export default function WeeklyPage() {
  const { sessionData, loading } = useDashboard()

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h2 className="text-2xl font-bold">Session Trends</h2>
        <p className="text-slate-500">Track each assessment session and compare changes over time</p>
      </div>
      <SessionTrends sessionData={sessionData} loading={loading.sessions} />
    </div>
  )
}
