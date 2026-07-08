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

const METRICS = [
  { key: 'avg_hr', label: 'Heart Rate', color: '#ef4444' },
  { key: 'steps', label: 'Steps', color: '#0ea5e9' },
  { key: 'sleep_duration_h', label: 'Sleep (hrs)', color: '#8b5cf6' },
  { key: 'stress', label: 'Stress', color: '#f59e0b' },
]

export default function TimeSeriesChart({ data, title, message, hasData, activeMetrics = ['avg_hr', 'steps', 'sleep_duration_h'] }) {
  if (!hasData) {
    return (
      <div className="health-card flex min-h-[280px] flex-col items-center justify-center text-center">
        <div className="mb-3 text-4xl opacity-30">📊</div>
        <p className="font-medium text-slate-600">No data available yet</p>
        <p className="mt-1 max-w-sm text-sm text-slate-400">
          {message || 'Log wearable readings or run an assessment to see trends.'}
        </p>
      </div>
    )
  }

  const lines = METRICS.filter((m) => activeMetrics.includes(m.key))

  return (
    <div className="health-card">
      <h3 className="mb-1 text-lg font-semibold">{title}</h3>
      {message && <p className="mb-4 text-sm text-amber-600">{message}</p>}
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
          <XAxis dataKey="date" tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip contentStyle={{ borderRadius: 12, border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,0.08)' }} />
          <Legend />
          {lines.map((m) => (
            <Line key={m.key} type="monotone" dataKey={m.key} name={m.label} stroke={m.color} strokeWidth={2} dot={false} />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
