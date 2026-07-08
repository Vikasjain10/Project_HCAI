import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { formatDate, getWellnessColor } from '../utils/colors'

const STRESS_AXIS_LABELS = { 1: 'Low', 2: 'Moderate', 3: 'High' }

function stressBadgeClass(stress) {
  const level = String(stress).toLowerCase()
  if (level.includes('high')) {
    return 'bg-red-100 text-red-700 dark:bg-red-950/50 dark:text-red-300'
  }
  if (level.includes('moderate') || level.includes('medium')) {
    return 'bg-amber-100 text-amber-700 dark:bg-amber-950/50 dark:text-amber-300'
  }
  return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300'
}

const statCardClass = 'rounded-xl bg-slate-50 p-4 dark:bg-slate-800/60'
const statLabelClass = 'text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400'
const statValueClass = 'mt-1 text-xl font-semibold capitalize text-slate-900 dark:text-slate-100'

function SessionChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  const point = payload[0]?.payload
  return (
    <div className="rounded-xl border border-slate-100 bg-white p-3 text-xs shadow-lg dark:border-slate-700 dark:bg-slate-800">
      <p className="font-medium text-slate-900 dark:text-slate-100">{label}</p>
      {point?.stress_label && (
        <p className="mt-1 text-slate-600 dark:text-slate-300">Stress: {point.stress_label}</p>
      )}
      {point?.wellness_score != null && (
        <p className="text-slate-600 dark:text-slate-300">Wellness: {point.wellness_score}/100</p>
      )}
    </div>
  )
}

export default function SessionTrends({ sessionData, loading }) {
  if (loading) {
    return <div className="health-card animate-pulse h-96" />
  }

  if (!sessionData?.has_data) {
    return (
      <div className="health-card">
        <p className="text-slate-500">{sessionData?.message || 'No sessions recorded yet.'}</p>
      </div>
    )
  }

  const { sessions, comparison, aggregates, chart_data: chartData } = sessionData

  return (
    <div className="space-y-6">
      {aggregates && (
        <div className="health-card space-y-5">
          <div>
            <h3 className="text-lg font-semibold">Session Overview</h3>
            <p className="text-sm text-slate-500">
              Averages across {aggregates.session_count} assessed session
              {aggregates.session_count === 1 ? '' : 's'}
            </p>
          </div>

          <div className="grid gap-3 sm:grid-cols-3">
            <div className={statCardClass}>
              <p className={statLabelClass}>Average stress</p>
              <p className={statValueClass}>
                {aggregates.average_stress_label ?? '—'}
              </p>
              {aggregates.average_stress_score != null && (
                <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                  Score {aggregates.average_stress_score} / 3
                </p>
              )}
            </div>
            <div className={statCardClass}>
              <p className={statLabelClass}>Average wellness</p>
              <p
                className={`mt-1 text-xl font-semibold ${
                  aggregates.average_wellness_score != null
                    ? getWellnessColor(aggregates.average_wellness_score).bg
                    : 'text-slate-900 dark:text-slate-100'
                }`}
              >
                {aggregates.average_wellness_score ?? '—'}
                {aggregates.average_wellness_score != null && (
                  <span className="text-sm font-normal text-slate-500 dark:text-slate-400"> /100</span>
                )}
              </p>
            </div>
            <div className={statCardClass}>
              <p className={statLabelClass}>Sessions assessed</p>
              <p className="mt-1 text-xl font-semibold text-slate-900 dark:text-slate-100">
                {aggregates.session_count}
              </p>
            </div>
          </div>

          {chartData?.length > 0 && (
            <div>
              <p className="mb-3 text-sm font-medium text-slate-600 dark:text-slate-300">
                Stress & wellness over time
              </p>
              <ResponsiveContainer width="100%" height={280}>
                <LineChart data={chartData} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="label" tick={{ fontSize: 11 }} />
                  <YAxis
                    yAxisId="stress"
                    domain={[1, 3]}
                    ticks={[1, 2, 3]}
                    tickFormatter={(v) => STRESS_AXIS_LABELS[v] || v}
                    tick={{ fontSize: 11 }}
                    width={72}
                  />
                  <YAxis
                    yAxisId="wellness"
                    orientation="right"
                    domain={[0, 100]}
                    tick={{ fontSize: 11 }}
                    width={40}
                  />
                  <Tooltip content={<SessionChartTooltip />} />
                  <Legend />
                  <Line
                    yAxisId="stress"
                    type="monotone"
                    dataKey="stress_score"
                    name="Stress level"
                    stroke="#6366f1"
                    strokeWidth={2}
                    dot={{ r: 4 }}
                    connectNulls
                  />
                  <Line
                    yAxisId="wellness"
                    type="monotone"
                    dataKey="wellness_score"
                    name="Wellness score"
                    stroke="#10b981"
                    strokeWidth={2}
                    dot={{ r: 4 }}
                    connectNulls
                  />
                </LineChart>
              </ResponsiveContainer>
              <p className="mt-2 text-xs text-slate-400">
                Stress axis: Low → Moderate → High. Dates show most recent sessions chronologically.
              </p>
            </div>
          )}
        </div>
      )}

      {comparison && (
        <div className="health-card space-y-4">
          <div>
            <h3 className="text-lg font-semibold">Session Comparison</h3>
            <p className="text-sm text-slate-500">Current session vs your previous assessment</p>
          </div>
          <div className="rounded-2xl bg-indigo-50 p-4 text-sm text-indigo-900 dark:bg-indigo-950/40 dark:text-indigo-200">
            {comparison.summary}
          </div>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <div className={statCardClass}>
              <p className={statLabelClass}>Previous stress</p>
              <p className={statValueClass}>{comparison.previous_stress}</p>
            </div>
            <div className={statCardClass}>
              <p className={statLabelClass}>Current stress</p>
              <p className={statValueClass}>{comparison.current_stress}</p>
            </div>
            {comparison.aggregates?.average_stress_label && (
              <div className="rounded-xl bg-indigo-50 p-4 dark:bg-indigo-950/40">
                <p className="text-xs uppercase tracking-wide text-indigo-600 dark:text-indigo-300">
                  Overall avg stress
                </p>
                <p className="mt-1 text-xl font-semibold capitalize text-indigo-900 dark:text-indigo-100">
                  {comparison.aggregates.average_stress_label}
                </p>
                <p className="mt-1 text-xs text-indigo-700 dark:text-indigo-300">
                  {comparison.aggregates.average_stress_score} / 3 across{' '}
                  {comparison.aggregates.session_count} sessions
                </p>
              </div>
            )}
            {comparison.aggregates?.average_wellness_score != null && (
              <div className="rounded-xl bg-emerald-50 p-4 dark:bg-emerald-950/40">
                <p className="text-xs uppercase tracking-wide text-emerald-600 dark:text-emerald-300">
                  Overall avg wellness
                </p>
                <p className="mt-1 text-xl font-semibold text-emerald-900 dark:text-emerald-100">
                  {comparison.aggregates.average_wellness_score}
                </p>
              </div>
            )}
          </div>
          {comparison.feature_changes?.length > 0 && (
            <div className="space-y-2">
              <p className="text-sm font-medium text-slate-600 dark:text-slate-300">What changed</p>
              {comparison.feature_changes.map((change) => (
                <div
                  key={change.feature}
                  className="rounded-xl border border-slate-100 bg-white p-3 text-sm dark:border-slate-700 dark:bg-slate-800/60"
                >
                  <p className="font-medium capitalize text-slate-900 dark:text-slate-100">{change.label}</p>
                  <p className="text-slate-600 dark:text-slate-300">{change.message}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <div className="health-card">
        <h3 className="mb-4 text-lg font-semibold">Recent Sessions</h3>
        <div className="space-y-3">
          {sessions.map((session) => (
            <div
              key={session.id}
              className="rounded-xl border border-slate-100 p-4 dark:border-slate-700 dark:bg-slate-800/40"
            >
              <div className="flex flex-wrap items-center justify-between gap-2">
                <p className="font-medium text-slate-900 dark:text-slate-100">
                  {formatDate(session.created_at)}
                </p>
                <span
                  className={`rounded-full px-3 py-1 text-xs font-semibold capitalize ${stressBadgeClass(session.outputs.stress)}`}
                >
                  {session.outputs.stress} stress
                </span>
              </div>
              <div className="mt-3 grid gap-2 text-sm text-slate-600 dark:text-slate-300 sm:grid-cols-4">
                <span>Sleep: {session.inputs.sleep_duration_h ?? '—'}h</span>
                <span>Steps: {session.inputs.steps ?? '—'}</span>
                <span>HR: {session.inputs.avg_hr ?? '—'} bpm</span>
                <span>Wellness: {session.outputs.wellness_score ?? '—'}</span>
              </div>
              {(session.explanation?.stress?.summary || session.explanation?.summary) && (
                <p className="mt-3 rounded-lg bg-slate-50 p-3 text-xs text-slate-600 dark:bg-slate-900/50 dark:text-slate-300">
                  {session.explanation?.stress?.summary || session.explanation?.summary}
                </p>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
