import { NavLink, Outlet, useNavigate, Link } from 'react-router-dom'
import ThemeToggle from './ThemeToggle'
import UserProfileCard from './UserProfileCard'
import { APP_NAME, APP_TAGLINE } from '../constants/brand'
import { useAuth } from '../context/AuthContext'

const NAV = [
  { to: '/dashboard', end: true, label: 'Run Assessment', icon: '▶' },
  { to: '/dashboard/weekly', label: 'Session Trends', icon: '▦' },
  { to: '/dashboard/insights', label: 'Insights', icon: '✦' },
  { to: '/dashboard/profile', label: 'My Profile', icon: '👤' },
]

export default function DashboardLayout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-[#f5f5f7] dark:bg-slate-950">
      <div className="mx-auto flex max-w-[1400px]">
        <aside className="sticky top-0 hidden h-screen w-64 shrink-0 flex-col border-r border-slate-200/80 bg-white/70 p-6 backdrop-blur-xl dark:border-slate-800 dark:bg-slate-900/70 lg:flex">
          <div className="mb-10">
            <Link to="/" className="flex items-center gap-2">
              <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-sky-500 to-indigo-600 text-sm text-white">
                ♥
              </span>
              <div>
                <p className="text-sm font-bold text-slate-900 dark:text-white">{APP_NAME}</p>
                <p className="text-[10px] text-slate-500 dark:text-slate-400">{APP_TAGLINE}</p>
              </div>
            </Link>
            <p className="mt-4 truncate text-sm text-slate-500 dark:text-slate-400">{user?.name}</p>
            <div className="mt-3">
              <UserProfileCard compact />
            </div>
          </div>
          <nav className="flex flex-1 flex-col gap-1">
            {NAV.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition-all duration-200 ${
                    isActive
                      ? 'bg-slate-900 text-white shadow-md dark:bg-sky-600'
                      : 'text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800'
                  }`
                }
              >
                <span>{item.icon}</span>
                {item.label}
              </NavLink>
            ))}
          </nav>
          <div className="space-y-2">
            <ThemeToggle className="w-full justify-center" />
            <button
              onClick={handleLogout}
              className="w-full rounded-xl px-4 py-2.5 text-left text-sm text-slate-500 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
            >
              Sign out
            </button>
          </div>
        </aside>

        <div className="flex-1">
          <header className="sticky top-0 z-10 border-b border-slate-200/80 bg-[#f5f5f7]/90 px-4 py-4 backdrop-blur dark:border-slate-800 dark:bg-slate-950/90 lg:hidden">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-semibold dark:text-white">{user?.name}</p>
                <p className="text-xs text-slate-500">{APP_NAME}</p>
              </div>
              <div className="flex items-center gap-2">
                <ThemeToggle />
                <button onClick={handleLogout} className="text-sm text-slate-500">
                  Sign out
                </button>
              </div>
            </div>
            <nav className="mt-3 flex gap-2 overflow-x-auto pb-1">
              {NAV.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.end}
                  className={({ isActive }) =>
                    `whitespace-nowrap rounded-full px-3 py-1.5 text-xs font-medium ${
                      isActive
                        ? 'bg-slate-900 text-white dark:bg-sky-600'
                        : 'bg-white text-slate-600 dark:bg-slate-800 dark:text-slate-300'
                    }`
                  }
                >
                  {item.label}
                </NavLink>
              ))}
            </nav>
          </header>

          <main className="p-4 sm:p-6 lg:p-8">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  )
}
