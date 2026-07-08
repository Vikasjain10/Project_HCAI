import { Link, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import ThemeToggle from '../components/ThemeToggle'
import { APP_NAME, APP_TAGLINE } from '../constants/brand'
import { signup } from '../services/auth'

const ACTIVITY_LEVELS = [
  { value: 'sedentary', label: 'Sedentary (< 5k steps/day)' },
  { value: 'moderate', label: 'Moderate (5k–10k steps/day)' },
  { value: 'active', label: 'Active (10k+ steps/day)' },
]

const GENDERS = [
  { value: 'male', label: 'Male' },
  { value: 'female', label: 'Female' },
  { value: 'other', label: 'Other' },
  { value: 'prefer_not_to_say', label: 'Prefer not to say' },
]

export default function RegisterPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    age: '',
    gender: 'prefer_not_to_say',
    weight_kg: '',
    height_cm: '',
    activity_level: 'moderate',
    sleep_goal_h: '8',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const update = (key, value) => setForm((prev) => ({ ...prev, [key]: value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await signup({
        ...form,
        age: Number(form.age),
        weight_kg: Number(form.weight_kg),
        height_cm: Number(form.height_cm),
        sleep_goal_h: Number(form.sleep_goal_h),
      })
      navigate('/login?registered=1', { replace: true })
    } catch (err) {
      const detail = err.response?.data?.detail
      let message = 'Registration failed'
      if (Array.isArray(detail)) {
        message = detail.map((item) => item.msg || item).join(', ')
      } else if (typeof detail === 'string' && detail) {
        message = detail
      } else if (!err.response) {
        message = 'Cannot reach the server. Start the backend on port 8000.'
      }
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  const inputClass =
    'mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none focus:border-sky-400 dark:border-slate-600 dark:bg-slate-800'

  return (
    <div className="flex min-h-screen flex-col bg-[#f5f5f7] dark:bg-slate-950">
      <div className="flex justify-end p-4">
        <ThemeToggle />
      </div>
      <div className="flex flex-1 items-center justify-center px-4 py-10">
      <div className="w-full max-w-xl">
        <div className="mb-8 text-center">
          <Link to="/" className="inline-flex items-center gap-2">
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-sky-500 to-indigo-600 text-white">♥</span>
          </Link>
          <p className="mt-3 text-xs font-semibold uppercase tracking-widest text-sky-500">{APP_NAME}</p>
          <h1 className="mt-1 text-3xl font-bold text-slate-900 dark:text-white">Create account</h1>
          <p className="mt-2 text-slate-500">{APP_TAGLINE}</p>
        </div>

        <form onSubmit={handleSubmit} className="health-card space-y-4 shadow-xl shadow-slate-200/50 dark:shadow-none">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="sm:col-span-2">
              <label className="text-sm font-medium text-slate-600">Full name</label>
              <input type="text" required minLength={2} value={form.name} onChange={(e) => update('name', e.target.value)} className={inputClass} />
            </div>
            <div className="sm:col-span-2">
              <label className="text-sm font-medium text-slate-600">Email</label>
              <input type="email" required value={form.email} onChange={(e) => update('email', e.target.value)} className={inputClass} />
            </div>
            <div className="sm:col-span-2">
              <label className="text-sm font-medium text-slate-600">Password</label>
              <input type="password" required minLength={6} value={form.password} onChange={(e) => update('password', e.target.value)} className={inputClass} />
            </div>
            <div>
              <label className="text-sm font-medium text-slate-600">Age</label>
              <input type="number" required min={13} max={120} value={form.age} onChange={(e) => update('age', e.target.value)} className={inputClass} />
            </div>
            <div>
              <label className="text-sm font-medium text-slate-600">Gender</label>
              <select required value={form.gender} onChange={(e) => update('gender', e.target.value)} className={inputClass}>
                {GENDERS.map((g) => (
                  <option key={g.value} value={g.value}>{g.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-sm font-medium text-slate-600">Weight (kg)</label>
              <input type="number" required min={20} max={300} step="0.1" value={form.weight_kg} onChange={(e) => update('weight_kg', e.target.value)} className={inputClass} />
            </div>
            <div>
              <label className="text-sm font-medium text-slate-600">Height (cm)</label>
              <input type="number" required min={100} max={250} step="0.1" value={form.height_cm} onChange={(e) => update('height_cm', e.target.value)} className={inputClass} />
            </div>
            <div>
              <label className="text-sm font-medium text-slate-600">Activity level</label>
              <select required value={form.activity_level} onChange={(e) => update('activity_level', e.target.value)} className={inputClass}>
                {ACTIVITY_LEVELS.map((a) => (
                  <option key={a.value} value={a.value}>{a.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-sm font-medium text-slate-600">Sleep goal (hours)</label>
              <input type="number" required min={4} max={12} step="0.5" value={form.sleep_goal_h} onChange={(e) => update('sleep_goal_h', e.target.value)} className={inputClass} />
            </div>
          </div>

          {error && <p className="rounded-xl bg-red-50 px-3 py-2 text-sm text-red-600">{error}</p>}

          <button type="submit" disabled={loading} className="w-full rounded-xl bg-slate-900 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:opacity-60">
            {loading ? 'Creating account...' : 'Register'}
          </button>

          <p className="text-center text-sm text-slate-500">
            Already have an account?{' '}
            <Link to="/login" className="font-medium text-sky-600 hover:text-sky-700 dark:text-sky-400">Sign in</Link>
          </p>
          <p className="text-center text-xs text-slate-400">
            <Link to="/" className="hover:text-sky-600 dark:hover:text-sky-400">← Back to home</Link>
          </p>
        </form>
      </div>
      </div>
    </div>
  )
}
