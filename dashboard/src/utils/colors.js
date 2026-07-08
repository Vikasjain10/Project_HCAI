export function getStressColor(stress) {
  const level = String(stress).toLowerCase()
  if (level.includes('high')) return 'bg-red-500 text-white'
  if (level.includes('moderate') || level.includes('medium')) return 'bg-amber-500 text-white'
  return 'bg-emerald-500 text-white'
}

export function getWellnessColor(score) {
  if (score < 40) return { stroke: '#ef4444', label: 'Poor', bg: 'text-red-500' }
  if (score < 70) return { stroke: '#f59e0b', label: 'Moderate', bg: 'text-amber-500' }
  return { stroke: '#10b981', label: 'Good', bg: 'text-emerald-500' }
}

export function getRiskColor(risk) {
  const level = String(risk).toLowerCase()
  if (level === 'high') return 'bg-red-500/15 text-red-600 border-red-300 dark:text-red-400'
  if (level === 'medium') return 'bg-amber-500/15 text-amber-600 border-amber-300 dark:text-amber-400'
  return 'bg-emerald-500/15 text-emerald-600 border-emerald-300 dark:text-emerald-400'
}

export function formatDate(dateStr) {
  try {
    return new Date(dateStr).toLocaleString()
  } catch {
    return dateStr
  }
}
