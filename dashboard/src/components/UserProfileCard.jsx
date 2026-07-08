import { useAuth } from '../context/AuthContext'

const GENDER_LABELS = {
  male: 'Male',
  female: 'Female',
  other: 'Other',
  prefer_not_to_say: 'Prefer not to say',
}

function formatActivity(level) {
  if (!level) return '—'
  return level.charAt(0).toUpperCase() + level.slice(1)
}

function ProfileField({ label, value }) {
  return (
    <div className="rounded-xl bg-slate-50 px-4 py-3 dark:bg-slate-800/60">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">{label}</p>
      <p className="mt-1 text-sm font-semibold text-slate-900 dark:text-slate-100">{value ?? '—'}</p>
    </div>
  )
}

export default function UserProfileCard({ compact = false }) {
  const { user } = useAuth()

  if (!user) {
    return (
      <div className="health-card text-sm text-slate-500">Sign in to view your profile.</div>
    )
  }

  const fields = [
    { label: 'Full name', value: user.name },
    { label: 'Email', value: user.email },
    { label: 'Age', value: user.age != null ? `${user.age} years` : null },
    { label: 'Gender', value: GENDER_LABELS[user.gender] || user.gender },
    { label: 'Weight', value: user.weight_kg != null ? `${user.weight_kg} kg` : null },
    { label: 'Height', value: user.height_cm != null ? `${user.height_cm} cm` : null },
    { label: 'Activity level', value: formatActivity(user.activity_level) },
    { label: 'Sleep goal', value: user.sleep_goal_h != null ? `${user.sleep_goal_h} hours/night` : null },
  ]

  if (compact) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white/80 p-3 dark:border-slate-700 dark:bg-slate-800/50">
        <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Signed in as</p>
        <p className="mt-1 font-semibold text-slate-900 dark:text-white">{user.name}</p>
        <p className="truncate text-xs text-slate-500">{user.email}</p>
      </div>
    )
  }

  return (
    <div className="health-card space-y-4">
      <div>
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white">My profile</h3>
        <p className="text-sm text-slate-500">Registration details for your logged-in account</p>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {fields.map((field) => (
          <ProfileField key={field.label} label={field.label} value={field.value} />
        ))}
      </div>
    </div>
  )
}
