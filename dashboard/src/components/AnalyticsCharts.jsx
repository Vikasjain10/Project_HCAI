import {
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from 'recharts'

const STRESS_COLORS = {
  Low: '#10b981',
  Moderate: '#f59e0b',
  High: '#ef4444',
}

export default function AnalyticsCharts({ analytics, loading }) {
  if (loading) {
    return (
      <div className="card flex min-h-[320px] items-center justify-center text-slate-400">
        Loading analytics...
      </div>
    )
  }

  const sleepData = analytics?.sleep_vs_wellness || []
  const stepsData = analytics?.steps_vs_fatigue || []
  const stressData = analytics?.stress_distribution || []

  const hasData = sleepData.length > 0 || stepsData.length > 0 || stressData.length > 0

  if (!hasData) {
    return (
      <div className="card flex min-h-[320px] items-center justify-center text-slate-400">
        Run assessments to populate analytics charts
      </div>
    )
  }

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <div className="card lg:col-span-2">
        <h3 className="mb-4 font-semibold">Sleep vs Wellness Trend</h3>
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={sleepData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#33415533" />
            <XAxis dataKey="date" tick={{ fontSize: 12 }} />
            <YAxis yAxisId="left" tick={{ fontSize: 12 }} />
            <YAxis yAxisId="right" orientation="right" domain={[0, 100]} tick={{ fontSize: 12 }} />
            <Tooltip />
            <Legend />
            <Line yAxisId="left" type="monotone" dataKey="sleep" stroke="#0ea5e9" name="Sleep (hrs)" strokeWidth={2} />
            <Line yAxisId="right" type="monotone" dataKey="wellness" stroke="#8b5cf6" name="Wellness" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="card">
        <h3 className="mb-4 font-semibold">Stress Distribution</h3>
        <ResponsiveContainer width="100%" height={260}>
          <PieChart>
            <Pie data={stressData} dataKey="count" nameKey="stress" cx="50%" cy="50%" outerRadius={80} label>
              {stressData.map((entry) => (
                <Cell key={entry.stress} fill={STRESS_COLORS[entry.stress] || '#64748b'} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="card lg:col-span-3">
        <h3 className="mb-4 font-semibold">Steps vs Fatigue Correlation</h3>
        <ResponsiveContainer width="100%" height={260}>
          <ScatterChart>
            <CartesianGrid strokeDasharray="3 3" stroke="#33415533" />
            <XAxis type="number" dataKey="steps" name="Steps" tick={{ fontSize: 12 }} />
            <YAxis type="number" dataKey="fatigue" name="Fatigue" domain={[-0.1, 1.1]} ticks={[0, 1]} tick={{ fontSize: 12 }} />
            <ZAxis range={[80, 80]} />
            <Tooltip cursor={{ strokeDasharray: '3 3' }} />
            <Scatter data={stepsData} fill="#6366f1" />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
