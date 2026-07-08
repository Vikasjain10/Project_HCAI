import { useState } from 'react'
import { Link } from 'react-router-dom'
import ThemeToggle from '../components/ThemeToggle'
import { APP_NAME, APP_TAGLINE, APP_DESCRIPTION } from '../constants/brand'
import { useAuth } from '../context/AuthContext'

const HOW_IT_WORKS = [
  {
    icon: '📝',
    title: 'Register & sign in',
    text: 'Create your profile with age, activity level, and sleep goals so assessments are personalized.',
  },
  {
    icon: '⌚',
    title: 'Enter wearable metrics',
    text: 'Add heart rate, sleep, steps, and exercise from your watch or fitness tracker — plus optional self-reported readiness.',
  },
  {
    icon: '📊',
    title: 'Get instant insights',
    text: 'ML models estimate stress and fatigue; a wellness formula scores your overall balance with clear explanations.',
  },
]

const CALCULATION = [
  {
    title: 'Stress level (Low / Moderate / High)',
    text: 'Predicted by machine learning from sleep duration, activity (steps), physiological load (HR, RHR, sleep history), and average heart rate. Self-reported stress does not drive this model.',
  },
  {
    title: 'Fatigue (Yes / No) & type',
    text: 'Wearable-only model using heart rate, resting HR, sleep, deep sleep, steps, and exercise duration. Fatigue type categorizes the dominant pattern (General, Physical, Sleep, Stress).',
  },
  {
    title: 'Wellness score (0–100)',
    text: 'Weighted formula: sleep 30%, activity 25%, recovery (readiness) 25%, stress control 10%, exercise 10%. Compare trends across sessions over time.',
  },
]

const INDICATORS = [
  { name: 'Heart rate', normal: '60–100 bpm', note: 'Elevated HR may increase stress & fatigue scores' },
  { name: 'Resting heart rate', normal: '50–80 bpm', note: 'Used in physiological load' },
  { name: 'Sleep duration', normal: '7–9 hours', note: 'Compared to your personal sleep goal' },
  { name: 'Deep sleep', normal: '~90+ min', note: 'Low deep sleep affects fatigue' },
  { name: 'Daily steps', normal: '8,000–10,000+', note: 'Drives activity & wellness' },
  { name: 'Exercise duration', normal: '30–45 min', note: 'Very high load may signal fatigue' },
  { name: 'Readiness (self-report)', normal: '70–100', note: 'Wellness score only' },
  { name: 'Stress (self-report)', normal: 'Lower is better', note: 'Wellness “stress control” only' },
]

const FAQS = [
  {
    q: 'What is a good wellness score?',
    a: 'Scores 70+ indicate good balance. 40–69 suggest moderate wellness — focus on sleep and recovery. Below 50 triggers a wellness alert on your dashboard. Scores above 85 receive positive AI insights. These are estimates, not diagnoses.',
  },
  {
    q: 'What should my stress level be?',
    a: 'Low is ideal for recovery and focus. Moderate is common during busy periods. High suggests your wearables show strain — prioritize rest, sleep, and activity balance. Track changes across sessions.',
  },
  {
    q: 'Can VitalTrack diagnose medical conditions?',
    a: 'No. VitalTrack provides lifestyle and wellness estimates only. It is not FDA-cleared medical software. Always consult a doctor for symptoms or emergencies.',
  },
  {
    q: 'Why don’t my slider changes affect stress/fatigue?',
    a: 'Stress and fatigue models use wearable metrics only. Self-reported stress and readiness affect the wellness score, not the ML stress/fatigue predictions.',
  },
  {
    q: 'How often should I run an assessment?',
    a: 'Daily or after significant changes (poor sleep, heavy exercise, illness) gives the best session trends and averages.',
  },
  {
    q: 'When should I seek emergency care?',
    a: 'If wellness is critically low, stress is high with fatigue, or you have chest pain, fainting, severe shortness of breath, or other acute symptoms — call emergency services or visit a clinic immediately.',
  },
]

function FaqItem({ q, a }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="rounded-2xl border border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-900">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left"
      >
        <span className="font-medium text-slate-900 dark:text-slate-100">{q}</span>
        <span className="text-slate-400">{open ? '−' : '+'}</span>
      </button>
      {open && (
        <p className="border-t border-slate-100 px-5 py-4 text-sm leading-relaxed text-slate-600 dark:border-slate-800 dark:text-slate-400">
          {a}
        </p>
      )}
    </div>
  )
}

export default function HomePage() {
  const { isAuthenticated } = useAuth()

  return (
    <div className="min-h-screen bg-[#f5f5f7] dark:bg-slate-950">
      <header className="sticky top-0 z-20 border-b border-slate-200/80 bg-white/80 backdrop-blur-xl dark:border-slate-800 dark:bg-slate-950/80">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-6">
          <Link to="/" className="flex items-center gap-2">
            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-sky-500 to-indigo-600 text-lg text-white">
              ♥
            </span>
            <div>
              <p className="text-sm font-bold text-slate-900 dark:text-white">{APP_NAME}</p>
              <p className="text-[10px] text-slate-500 dark:text-slate-400">{APP_TAGLINE}</p>
            </div>
          </Link>
          <div className="flex items-center gap-3">
            <ThemeToggle />
            {isAuthenticated ? (
              <Link
                to="/dashboard"
                className="rounded-full bg-slate-900 px-4 py-2 text-sm font-medium text-white dark:bg-sky-600"
              >
                Dashboard
              </Link>
            ) : (
              <>
                <Link to="/login" className="text-sm font-medium text-slate-600 dark:text-slate-300">
                  Sign in
                </Link>
                <Link
                  to="/register"
                  className="rounded-full bg-slate-900 px-4 py-2 text-sm font-medium text-white dark:bg-sky-600"
                >
                  Get started
                </Link>
              </>
            )}
          </div>
        </div>
      </header>

      <section className="relative overflow-hidden px-4 py-16 sm:px-6 sm:py-24">
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-sky-100/50 via-transparent to-indigo-100/30 dark:from-sky-950/30 dark:to-indigo-950/20" />
        <div className="relative mx-auto max-w-4xl text-center">
          <p className="text-sm font-semibold uppercase tracking-widest text-sky-600 dark:text-sky-400">
            {APP_TAGLINE}
          </p>
          <h1 className="mt-4 text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl dark:text-white">
            Your insights into wellness &amp; risk levels
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-600 dark:text-slate-400">
            {APP_DESCRIPTION}
          </p>
          <div className="mt-10 flex flex-wrap justify-center gap-4">
            {isAuthenticated ? (
              <Link
                to="/dashboard"
                className="inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-sky-500 to-indigo-600 px-8 py-3.5 text-sm font-semibold text-white shadow-lg shadow-sky-500/25"
              >
                <span className="text-lg">▶</span> Run your assessment
              </Link>
            ) : (
              <>
                <Link
                  to="/login"
                  className="inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-sky-500 to-indigo-600 px-8 py-3.5 text-sm font-semibold text-white shadow-lg shadow-sky-500/25"
                >
                  Sign in to assess
                </Link>
                <Link
                  to="/register"
                  className="rounded-full border border-slate-300 bg-white px-8 py-3.5 text-sm font-semibold text-slate-700 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-200"
                >
                  Create free account
                </Link>
              </>
            )}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-12 sm:px-6">
        <h2 className="text-center text-2xl font-bold text-slate-900 dark:text-white">How it works</h2>
        <div className="mt-10 grid gap-6 md:grid-cols-3">
          {HOW_IT_WORKS.map((step) => (
            <div key={step.title} className="health-card text-center">
              <span className="text-4xl">{step.icon}</span>
              <h3 className="mt-4 font-semibold text-slate-900 dark:text-white">{step.title}</h3>
              <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">{step.text}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="bg-white py-16 dark:bg-slate-900/50">
        <div className="mx-auto max-w-6xl px-4 sm:px-6">
          <h2 className="text-center text-2xl font-bold text-slate-900 dark:text-white">
            How it&apos;s calculated
          </h2>
          <p className="mx-auto mt-3 max-w-2xl text-center text-sm text-slate-600 dark:text-slate-400">
            Measure on a consistent basis under similar conditions so you can monitor trends over time.
          </p>
          <div className="mt-10 space-y-4">
            {CALCULATION.map((item) => (
              <div key={item.title} className="health-card">
                <h3 className="font-semibold text-sky-700 dark:text-sky-400">{item.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-600 dark:text-slate-400">{item.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
        <h2 className="text-center text-2xl font-bold text-slate-900 dark:text-white">
          Health indicators we use
        </h2>
        <div className="mt-8 overflow-x-auto rounded-2xl border border-slate-200 dark:border-slate-700">
          <table className="w-full min-w-[640px] text-left text-sm">
            <thead className="bg-slate-50 dark:bg-slate-800">
              <tr>
                <th className="px-4 py-3 font-semibold text-slate-700 dark:text-slate-200">Indicator</th>
                <th className="px-4 py-3 font-semibold text-slate-700 dark:text-slate-200">Typical range</th>
                <th className="px-4 py-3 font-semibold text-slate-700 dark:text-slate-200">In this app</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {INDICATORS.map((row) => (
                <tr key={row.name} className="bg-white dark:bg-slate-900">
                  <td className="px-4 py-3 font-medium text-slate-900 dark:text-slate-100">{row.name}</td>
                  <td className="px-4 py-3 text-slate-600 dark:text-slate-400">{row.normal}</td>
                  <td className="px-4 py-3 text-slate-600 dark:text-slate-400">{row.note}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="bg-slate-100 py-16 dark:bg-slate-900">
        <div className="mx-auto max-w-3xl px-4 sm:px-6">
          <h2 className="text-center text-2xl font-bold text-slate-900 dark:text-white">FAQs</h2>
          <div className="mt-8 space-y-3">
            {FAQS.map((item) => (
              <FaqItem key={item.q} q={item.q} a={item.a} />
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-4xl px-4 py-16 text-center sm:px-6">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Ready to track your wellness?</h2>
        <p className="mt-3 text-slate-600 dark:text-slate-400">
          Sign in and run your first assessment in under a minute.
        </p>
        <Link
          to={isAuthenticated ? '/dashboard' : '/login'}
          className="mt-6 inline-block rounded-full bg-slate-900 px-8 py-3 text-sm font-semibold text-white dark:bg-sky-600"
        >
          {isAuthenticated ? 'Run assessment' : 'Sign in now'}
        </Link>
      </section>

      <footer className="border-t border-slate-200 px-4 py-8 text-center text-xs text-slate-500 dark:border-slate-800 dark:text-slate-500">
        <p>
          © {new Date().getFullYear()} {APP_NAME} — {APP_TAGLINE}. Not for medical diagnosis.
        </p>
      </footer>
    </div>
  )
}
