import { getWellnessColor } from '../utils/colors'

export default function WellnessGauge({ score }) {
  if (score == null) {
    return (
      <div className="health-card flex h-full min-h-[220px] items-center justify-center text-slate-400">
        Wellness score will appear here
      </div>
    )
  }

  const { stroke, label, bg } = getWellnessColor(score)
  const radius = 70
  const circumference = 2 * Math.PI * radius
  const progress = Math.min(100, Math.max(0, score))
  const offset = circumference - (progress / 100) * circumference

  return (
    <div className="health-card flex h-full flex-col items-center justify-center">
      <h2 className="mb-4 w-full text-xl font-semibold">Wellness Score</h2>
      <div className="relative">
        <svg width="180" height="180" className="-rotate-90">
          <circle cx="90" cy="90" r={radius} fill="none" stroke="#e2e8f0" strokeWidth="12" />
          <circle
            cx="90"
            cy="90"
            r={radius}
            fill="none"
            stroke={stroke}
            strokeWidth="12"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            className="transition-all duration-700"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`text-4xl font-bold ${bg}`}>{score}</span>
          <span className="text-sm text-slate-500">{label}</span>
        </div>
      </div>
    </div>
  )
}
