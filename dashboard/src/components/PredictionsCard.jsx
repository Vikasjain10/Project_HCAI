import { useState } from 'react'
import { getWellnessColor } from '../utils/colors'

const STRESS_DRIVER_LABELS = {
  sleep_duration_h: 'Sleep duration',
  activity_level: 'Activity level',
  stress_history: 'Physiological load',
  avg_hr: 'Heart rate',
}

const FATIGUE_DRIVER_LABELS = {
  avg_hr: 'Average heart rate',
  rhr: 'Resting heart rate',
  sleep_duration_h: 'Sleep duration',
  deep_sleep_in_minutes: 'Deep sleep',
  steps: 'Daily steps',
  exercise_duration: 'Exercise duration',
}

const ACTIVITY_LABELS = { 0: 'Sedentary', 1: 'Moderate', 2: 'Active' }

const FATIGUE_TYPE_INFO = {
  General: 'Mixed signals from your wearable metrics — no single dominant driver.',
  Physical: 'Often linked to activity patterns — low movement or very high exercise load.',
  Sleep: 'Primarily driven by insufficient sleep or low deep-sleep minutes.',
  Stress: 'Associated with elevated heart rate and physiological load.',
}

const WELLNESS_LABELS = {
  sleep: { label: 'Sleep', hint: 'Compared to your sleep goal' },
  activity: { label: 'Activity (steps)', hint: 'Based on 10,000 steps target' },
  recovery: { label: 'Recovery (readiness)', hint: 'Self-reported readiness' },
  stress_control: { label: 'Stress control', hint: 'Lower self-reported stress = higher score' },
  exercise: { label: 'Exercise', hint: 'Based on 45 min target' },
}

function ProgressBar({ value, max = 100, color = 'bg-sky-500' }) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100))
  return (
    <div className="h-2 overflow-hidden rounded-full bg-slate-100">
      <div
        className={`h-full rounded-full transition-all duration-500 ${color}`}
        style={{ width: `${pct}%` }}
      />
    </div>
  )
}

function DetailPanel({ title, subtitle, children, onClose }) {
  return (
    <div className="animate-fade-in mt-4 overflow-hidden rounded-2xl border border-sky-100 bg-gradient-to-br from-sky-50/80 to-white p-5 shadow-inner">
      <div className="mb-4 flex items-start justify-between gap-3">
        <div>
          <h3 className="font-semibold text-slate-900">{title}</h3>
          {subtitle && <p className="mt-1 text-sm text-slate-500">{subtitle}</p>}
        </div>
        <button
          type="button"
          onClick={onClose}
          className="rounded-lg px-2 py-1 text-xs text-slate-400 hover:bg-slate-100 hover:text-slate-600"
          aria-label="Close details"
        >
          ✕
        </button>
      </div>
      {children}
    </div>
  )
}

function Tile({ id, active, onSelect, icon, label, value, valueClass, hint, children }) {
  const isActive = active === id
  return (
    <button
      type="button"
      onClick={() => onSelect(isActive ? null : id)}
      className={`group w-full rounded-2xl border p-4 text-left transition-all duration-200 ${
        isActive
          ? 'border-sky-400 bg-sky-50/60 shadow-md ring-2 ring-sky-200'
          : 'border-slate-100 bg-slate-50/80 hover:border-sky-200 hover:bg-white hover:shadow-sm'
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <span className="text-lg">{icon}</span>
        <span
          className={`text-[10px] font-medium uppercase tracking-wider text-slate-400 transition group-hover:text-sky-500 ${
            isActive ? 'text-sky-600' : ''
          }`}
        >
          {isActive ? 'Hide' : 'Details'}
        </span>
      </div>
      <p className="mt-2 text-xs font-medium text-slate-500">{label}</p>
      <p className={`mt-1 text-lg font-semibold capitalize ${valueClass || 'text-slate-900'}`}>{value}</p>
      {hint && <p className="mt-1 text-[11px] text-slate-400">{hint}</p>}
      {children}
    </button>
  )
}

function stressTextColor(stress) {
  const level = String(stress).toLowerCase()
  if (level.includes('high')) return 'text-red-600'
  if (level.includes('moderate') || level.includes('medium')) return 'text-amber-600'
  return 'text-emerald-600'
}

function formatStressFeature(key, value) {
  if (key === 'activity_level') return ACTIVITY_LABELS[Math.round(value)] || value
  if (key === 'sleep_duration_h') return `${value} hrs`
  if (key === 'avg_hr') return `${value} bpm`
  if (key === 'stress_history') return `${value}/100 load`
  return value
}

function stressBarValue(key, value) {
  if (key === 'sleep_duration_h') return Math.min(100, (value / 8) * 100)
  if (key === 'activity_level') return (value / 2) * 100
  if (key === 'stress_history') return value
  if (key === 'avg_hr') return Math.min(100, Math.max(0, ((value - 50) / 50) * 100))
  return 50
}

function stressBarColor(key, value) {
  if (key === 'sleep_duration_h' && value < 6) return 'bg-amber-500'
  if (key === 'stress_history' && value > 50) return 'bg-red-500'
  if (key === 'avg_hr' && value > 75) return 'bg-orange-500'
  return 'bg-emerald-500'
}

export default function PredictionsCard({
  predictions,
  stressFeatures,
  fatigueFeatures,
  wellnessBreakdown,
  wellnessScore,
}) {
  const [active, setActive] = useState(null)

  if (!predictions) {
    return (
      <div className="health-card flex min-h-[280px] flex-col items-center justify-center text-center text-slate-400">
        <span className="mb-2 text-3xl opacity-40">◉</span>
        <p className="text-sm">Run an assessment to see interactive results</p>
        <p className="mt-1 text-xs">Tap any tile below to explore model inputs</p>
      </div>
    )
  }

  const wellness = wellnessScore ?? null
  const wellnessColors = wellness != null ? getWellnessColor(wellness) : null

  return (
    <div className="health-card space-y-4">
      <div>
        <h2 className="text-xl font-semibold dark:text-white">Assessment Results</h2>
        <p className="text-xs text-slate-500">Click a tile to see model inputs — explanations appear below</p>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <Tile
          id="stress"
          active={active}
          onSelect={setActive}
          icon="🧠"
          label="Stress level"
          value={predictions.stress}
          valueClass={stressTextColor(predictions.stress)}
          hint={predictions.stress_confidence ? `${Math.round(predictions.stress_confidence * 100)}% confidence` : 'Wearable-driven ML'}
        />
        <Tile
          id="fatigue"
          active={active}
          onSelect={setActive}
          icon="⚡"
          label="Fatigue"
          value={predictions.fatigue === 1 ? 'Yes' : 'No'}
          valueClass={predictions.fatigue === 1 ? 'text-orange-600' : 'text-emerald-600'}
          hint="From HR, sleep, steps & exercise"
        />
        <Tile
          id="fatigue_type"
          active={active}
          onSelect={setActive}
          icon="🏷️"
          label="Fatigue type"
          value={predictions.fatigue_type}
          hint="Tap to learn what this means"
        />
        <Tile
          id="wellness"
          active={active}
          onSelect={setActive}
          icon="💚"
          label="Wellness score"
          value={wellness != null ? `${wellness}/100` : '—'}
          valueClass={wellnessColors?.bg || 'text-slate-900'}
          hint={wellnessColors?.label || 'Includes self-report factors'}
        />
      </div>

      {active === 'stress' && stressFeatures && (
        <DetailPanel
          title="Stress model inputs"
          subtitle="These wearable metrics determined your stress level — not self-reported stress."
          onClose={() => setActive(null)}
        >
          <div className="space-y-4">
            {Object.entries(stressFeatures).map(([key, value]) => (
              <div key={key}>
                <div className="mb-1 flex justify-between text-sm">
                  <span className="text-slate-700">{STRESS_DRIVER_LABELS[key] || key}</span>
                  <span className="font-medium text-slate-900">{formatStressFeature(key, value)}</span>
                </div>
                <ProgressBar
                  value={stressBarValue(key, value)}
                  color={stressBarColor(key, value)}
                />
              </div>
            ))}
          </div>
        </DetailPanel>
      )}

      {active === 'fatigue' && fatigueFeatures && (
        <DetailPanel
          title="Fatigue model inputs"
          subtitle="Wearable-only features — readiness and self-reported stress are excluded."
          onClose={() => setActive(null)}
        >
          <div className="grid gap-3 sm:grid-cols-2">
            {Object.entries(fatigueFeatures).map(([key, value]) => (
              <div
                key={key}
                className="rounded-xl border border-white bg-white/80 px-3 py-3 shadow-sm"
              >
                <p className="text-xs text-slate-500">{FATIGUE_DRIVER_LABELS[key] || key}</p>
                <p className="mt-1 text-base font-semibold text-slate-900">
                  {value}
                  {key.includes('hr') ? ' bpm' : key === 'sleep_duration_h' ? ' hrs' : key.includes('minutes') || key.includes('duration') ? ' min' : key === 'steps' ? ' steps' : ''}
                </p>
              </div>
            ))}
          </div>
          {predictions.fatigue_confidence != null && (
            <p className="mt-4 text-xs text-slate-500">
              Model confidence: {Math.round(predictions.fatigue_confidence * 100)}%
            </p>
          )}
        </DetailPanel>
      )}

      {active === 'fatigue_type' && (
        <DetailPanel
          title={`Fatigue type: ${predictions.fatigue_type}`}
          subtitle="Category assigned by the ML model based on your wearable pattern."
          onClose={() => setActive(null)}
        >
          <p className="text-sm leading-relaxed text-slate-700">
            {FATIGUE_TYPE_INFO[predictions.fatigue_type] ||
              'This category reflects the dominant pattern in your current metrics.'}
          </p>
          {fatigueFeatures && (
            <div className="mt-4 rounded-xl bg-white/70 p-3 text-xs text-slate-600">
              <p className="font-medium text-slate-800">Key signals this session</p>
              <ul className="mt-2 space-y-1">
                <li>Sleep: {fatigueFeatures.sleep_duration_h}h · Deep sleep: {fatigueFeatures.deep_sleep_in_minutes} min</li>
                <li>Steps: {fatigueFeatures.steps} · Exercise: {fatigueFeatures.exercise_duration} min</li>
                <li>HR: {fatigueFeatures.avg_hr} bpm (resting {fatigueFeatures.rhr} bpm)</li>
              </ul>
            </div>
          )}
        </DetailPanel>
      )}

      {active === 'wellness' && wellnessBreakdown && (
        <DetailPanel
          title="Wellness score breakdown"
          subtitle="Wellness includes self-reported stress & readiness unlike stress/fatigue ML."
          onClose={() => setActive(null)}
        >
          <div className="space-y-4">
            {Object.entries(wellnessBreakdown).map(([key, value]) => {
              const meta = WELLNESS_LABELS[key] || { label: key, hint: '' }
              const barColor =
                value >= 70 ? 'bg-emerald-500' : value >= 40 ? 'bg-amber-500' : 'bg-red-500'
              return (
                <div key={key}>
                  <div className="mb-1 flex justify-between text-sm">
                    <span className="text-slate-700">{meta.label}</span>
                    <span className="font-medium text-slate-900">{value}/100</span>
                  </div>
                  <ProgressBar value={value} color={barColor} />
                  {meta.hint && <p className="mt-1 text-[11px] text-slate-400">{meta.hint}</p>}
                </div>
              )
            })}
          </div>
          {wellness != null && (
            <div className="mt-4 flex items-center justify-between rounded-xl bg-white/70 px-4 py-3">
              <span className="text-sm font-medium text-slate-600">Overall wellness</span>
              <span className={`text-2xl font-bold ${wellnessColors?.bg}`}>{wellness}</span>
            </div>
          )}
        </DetailPanel>
      )}
    </div>
  )
}
