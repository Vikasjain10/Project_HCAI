import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

const VARIANTS = {
  stress: {
    title: 'Why this stress level?',
    emptyTitle: 'Stress explanation',
    emptyText: 'Run an assessment to see how each feature impacts your stress prediction.',
    increaseKey: 'increases_stress',
    reduceKey: 'reduces_stress',
    increaseColor: '#ef4444',
    reduceColor: '#10b981',
    increaseLabel: 'Increases stress',
    reduceLabel: 'Reduces stress',
    increaseCard: 'border-red-100 bg-red-50/50 dark:border-red-900/40 dark:bg-red-950/30',
    reduceCard: 'border-emerald-100 bg-emerald-50/50 dark:border-emerald-900/40 dark:bg-emerald-950/30',
    chartLabel: 'Feature impact on stress prediction',
  },
  fatigue: {
    title: 'Why this fatigue result?',
    emptyTitle: 'Fatigue explanation',
    emptyText: 'Run an assessment to see how wearables drove the fatigue prediction.',
    increaseKey: 'increases_fatigue',
    reduceKey: 'reduces_fatigue',
    increaseColor: '#f97316',
    reduceColor: '#10b981',
    increaseLabel: 'Pushes toward fatigue',
    reduceLabel: 'Lowers fatigue likelihood',
    increaseCard: 'border-orange-100 bg-orange-50/50 dark:border-orange-900/40 dark:bg-orange-950/30',
    reduceCard: 'border-emerald-100 bg-emerald-50/50 dark:border-emerald-900/40 dark:bg-emerald-950/30',
    chartLabel: 'Feature impact on fatigue prediction',
  },
  wellness: {
    title: 'Why this wellness score?',
    emptyTitle: 'Wellness explanation',
    emptyText: 'Run an assessment to see which drivers help or hurt your wellness score.',
    increaseKey: 'increases_wellness',
    reduceKey: 'reduces_wellness',
    increaseColor: '#10b981',
    reduceColor: '#ef4444',
    increaseLabel: 'Boosts wellness',
    reduceLabel: 'Lowers wellness',
    increaseCard: 'border-emerald-100 bg-emerald-50/50 dark:border-emerald-900/40 dark:bg-emerald-950/30',
    reduceCard: 'border-red-100 bg-red-50/50 dark:border-red-900/40 dark:bg-red-950/30',
    chartLabel: 'Driver impact on wellness score',
  },
}

export default function FeatureExplanation({
  explanation,
  variant = 'stress',
  compact = false,
  column = false,
  title,
  className = '',
}) {
  const config = VARIANTS[variant] || VARIANTS.stress
  const displayTitle = title || config.title

  if (!explanation) {
    if (compact) return null
    return (
      <div className={`health-card ${className}`}>
        <h3 className="text-lg font-semibold">{config.emptyTitle}</h3>
        <p className="mt-2 text-sm text-slate-500">{config.emptyText}</p>
      </div>
    )
  }

  const impacts = explanation.feature_impacts || []
  const chartData = impacts.map((item) => ({
    name: item.label,
    impact: Math.abs(item.shap_value),
    signed: item.shap_value,
    direction: item.direction,
    message: item.message,
  }))

  const wrapperClass = compact
    ? `space-y-4 ${className}`
    : `health-card space-y-5 ${column ? 'h-full' : ''} ${className}`

  return (
    <div className={wrapperClass}>
      <div>
        <h3 className={compact ? 'text-base font-semibold text-slate-900 dark:text-slate-100' : 'text-lg font-semibold text-slate-900 dark:text-slate-100'}>
          {displayTitle}
        </h3>
        {explanation.model_type && (
          <p className="text-xs text-slate-500 dark:text-slate-400">{explanation.model_type}</p>
        )}
      </div>

      <div
        className={`rounded-2xl bg-slate-50 text-sm leading-relaxed text-slate-700 dark:bg-slate-800/60 dark:text-slate-200 ${
          compact ? 'p-3' : 'p-4'
        }`}
      >
        {explanation.summary}
      </div>

      {chartData.length > 0 && (
        <div>
          <p className="mb-3 text-sm font-medium text-slate-600 dark:text-slate-300">{config.chartLabel}</p>
          <ResponsiveContainer width="100%" height={compact ? 180 : column ? 200 : 220}>
            <BarChart data={chartData} layout="vertical" margin={{ left: 4, right: 12 }}>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" />
              <XAxis type="number" tick={{ fontSize: 10 }} />
              <YAxis
                type="category"
                dataKey="name"
                width={column ? 88 : compact ? 95 : 110}
                tick={{ fontSize: 10 }}
              />
              <Tooltip
                formatter={(value, _name, props) => [props.payload.message, 'Impact']}
                contentStyle={{ borderRadius: 12, border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,0.08)' }}
              />
              <Bar dataKey="impact" radius={[0, 6, 6, 0]}>
                {chartData.map((entry) => (
                  <Cell
                    key={entry.name}
                    fill={
                      entry.direction === config.increaseKey
                        ? config.increaseColor
                        : config.reduceColor
                    }
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <div className="mt-2 flex flex-wrap gap-4 text-xs text-slate-500 dark:text-slate-400">
            <span className="flex items-center gap-1">
              <span
                className="h-2 w-2 rounded-full"
                style={{ backgroundColor: config.increaseColor }}
              />
              {config.increaseLabel}
            </span>
            <span className="flex items-center gap-1">
              <span
                className="h-2 w-2 rounded-full"
                style={{ backgroundColor: config.reduceColor }}
              />
              {config.reduceLabel}
            </span>
          </div>
        </div>
      )}

      <div className={`grid gap-3 ${column || compact ? 'grid-cols-1' : 'sm:grid-cols-2'}`}>
        {impacts.map((item) => (
          <div
            key={item.feature}
            className={`rounded-xl border p-3 text-sm ${
              item.direction === config.increaseKey ? config.increaseCard : config.reduceCard
            }`}
          >
            <p className="font-medium text-slate-900 dark:text-slate-100">{item.label}</p>
            <p className="mt-1 text-slate-600 dark:text-slate-300">{item.display_value}</p>
            <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">{item.message}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
