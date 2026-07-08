import { useDashboard } from '../context/DashboardContext'
import UserProfileCard from '../components/UserProfileCard'

export default function ProfilePage() {
  const { summary } = useDashboard()

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white">My account</h2>
        <p className="text-slate-500">Your login and registration details</p>
      </div>
      <UserProfileCard />
      {summary?.session_count != null && (
        <div className="health-card">
          <p className="text-sm text-slate-500">Activity on this account</p>
          <p className="mt-1 text-lg font-semibold text-slate-900 dark:text-white">
            {summary.session_count} assessment session{summary.session_count === 1 ? '' : 's'} recorded
          </p>
        </div>
      )}
    </div>
  )
}
