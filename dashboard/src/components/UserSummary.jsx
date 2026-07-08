import { formatDate, getRiskColor } from '../utils/colors'

export default function UserSummary({ summary, loading }) {
  if (loading) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="health-card animate-pulse h-28" />
        ))}
      </div>
    )
  }

  const cards = [
    {
      label: 'Sleep',
      value: summary?.sleep_hours != null ? `${summary.sleep_hours}h` : '—',
      sub: summary?.sleep_goal_h ? `Goal ${summary.sleep_goal_h}h` : 'Latest session',
      gradient: 'from-sky-400/20 to-indigo-400/10',
    },
    {
      label: 'Stress Score',
      value: summary?.health_status || 'No data',
      sub: summary?.stress_score != null ? `Input ${summary.stress_score}/100` : 'Run assessment',
      gradient: 'from-rose-400/20 to-orange-400/10',
    },
    {
      label: 'Activity',
      value: summary?.activity_steps != null ? `${Math.round(summary.activity_steps)} steps` : '—',
      sub: summary?.activity_level ? `${summary.activity_level} profile` : 'Latest session',
      gradient: 'from-emerald-400/20 to-teal-400/10',
    },
    {
      label: 'Sessions',
      value: summary?.session_count ?? 0,
      sub: summary?.last_updated ? `Updated ${formatDate(summary.last_updated)}` : 'No assessments yet',
      gradient: 'from-violet-400/20 to-purple-400/10',
    },
  ]

  return (
    <div className="space-y-4">
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {cards.map((card) => (
          <div key={card.label} className={`health-card bg-gradient-to-br ${card.gradient}`}>
            <p className="text-xs font-medium uppercase tracking-wider text-slate-500">{card.label}</p>
            <p className="mt-2 text-2xl font-semibold text-slate-900">{card.value}</p>
            <p className="mt-1 text-sm text-slate-500">{card.sub}</p>
          </div>
        ))}
      </div>

      {summary?.wellness_score != null && (
        <div className="health-card flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-sm text-slate-500">Latest prediction</p>
            <p className="text-lg font-semibold text-slate-900">
              Wellness {summary.wellness_score}/100 · Risk {summary.risk_score || 'Unknown'}
            </p>
          </div>
          {summary?.risk_score && (
            <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${getRiskColor(summary.risk_score)}`}>
              {summary.risk_score}
            </span>
          )}
        </div>
      )}
    </div>
  )
}
