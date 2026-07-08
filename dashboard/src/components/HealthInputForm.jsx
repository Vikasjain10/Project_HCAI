const FIELDS = [
  { key: 'avg_hr', label: 'Average Heart Rate', unit: 'bpm', min: 40, max: 200, step: 1 },
  { key: 'rhr', label: 'Resting Heart Rate', unit: 'bpm', min: 30, max: 120, step: 1 },
  { key: 'sleep_duration_h', label: 'Sleep Duration', unit: 'hrs', min: 0, max: 16, step: 0.5 },
  { key: 'deep_sleep_in_minutes', label: 'Deep Sleep', unit: 'min', min: 0, max: 300, step: 5 },
  { key: 'steps', label: 'Daily Steps', unit: 'steps', min: 0, max: 50000, step: 100 },
  { key: 'exercise_duration', label: 'Exercise Duration', unit: 'min', min: 0, max: 300, step: 5 },
  { key: 'stress', label: 'Self-reported Stress', unit: '/100', min: 0, max: 100, step: 1 },
  { key: 'readiness', label: 'Readiness Score', unit: '/100', min: 0, max: 100, step: 1 },
]

export default function HealthInputForm({ values, onChange, onSubmit, loading, errors }) {
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault()
        onSubmit()
      }}
      className="health-card space-y-5"
    >
      <div>
        <h2 className="text-xl font-semibold">Wearable Health Input</h2>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Enter your daily metrics to run ML assessment
        </p>
      </div>

      <div className="grid gap-5 sm:grid-cols-2">
        {FIELDS.map((field) => (
          <div key={field.key} className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <label htmlFor={field.key} className="font-medium">
                {field.label}
              </label>
              <span className="text-medical-600 dark:text-medical-100">
                {values[field.key]} {field.unit}
              </span>
            </div>
            <input
              id={field.key}
              type="range"
              min={field.min}
              max={field.max}
              step={field.step}
              value={values[field.key]}
              onChange={(e) => onChange(field.key, Number(e.target.value))}
              className="h-2 w-full cursor-pointer appearance-none rounded-lg bg-slate-200 accent-sky-500 dark:bg-slate-700"
            />
            <input
              type="number"
              min={field.min}
              max={field.max}
              step={field.step}
              value={values[field.key]}
              onChange={(e) => onChange(field.key, Number(e.target.value))}
              className="w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800"
            />
            {errors[field.key] && (
              <p className="text-xs text-red-500">{errors[field.key]}</p>
            )}
          </div>
        ))}
      </div>

      {errors.general && (
        <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600 dark:bg-red-950/40 dark:text-red-400">
          {errors.general}
        </p>
      )}

      <button
        type="submit"
        disabled={loading}
        className="w-full rounded-full bg-slate-900 px-4 py-3 font-semibold text-white shadow-lg transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {loading ? 'Running Assessment...' : 'Run Full Assessment'}
      </button>
    </form>
  )
}
