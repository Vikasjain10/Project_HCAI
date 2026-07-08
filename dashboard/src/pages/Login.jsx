import { Link, useNavigate, useSearchParams } from 'react-router-dom'

import { useState } from 'react'

import ThemeToggle from '../components/ThemeToggle'

import { APP_NAME, APP_TAGLINE } from '../constants/brand'

import { login } from '../services/auth'

import { useAuth } from '../context/AuthContext'



export default function LoginPage() {

  const navigate = useNavigate()

  const { setUser } = useAuth()

  const [searchParams] = useSearchParams()

  const registered = searchParams.get('registered') === '1'



  const [email, setEmail] = useState('')

  const [password, setPassword] = useState('')

  const [error, setError] = useState('')

  const [loading, setLoading] = useState(false)



  const handleSubmit = async (e) => {

    e.preventDefault()

    setError('')

    setLoading(true)

    try {

      const data = await login(email, password)

      setUser(data.user)

      navigate('/dashboard', { replace: true })

    } catch (err) {

      const detail = err.response?.data?.detail

      let message = 'Authentication failed'

      if (typeof detail === 'string' && detail) message = detail

      else if (!err.response) message = 'Cannot reach the server. Start the backend on port 8000.'

      setError(message)

    } finally {

      setLoading(false)

    }

  }



  return (

    <div className="flex min-h-screen flex-col bg-[#f5f5f7] dark:bg-slate-950">

      <div className="flex justify-end p-4">

        <ThemeToggle />

      </div>

      <div className="flex flex-1 items-center justify-center px-4 pb-12">

        <div className="w-full max-w-md">

          <div className="mb-8 text-center">

            <Link to="/" className="inline-flex items-center gap-2">

              <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-sky-500 to-indigo-600 text-white">

                ♥

              </span>

            </Link>

            <p className="mt-3 text-xs font-semibold uppercase tracking-widest text-sky-500">{APP_NAME}</p>

            <h1 className="mt-1 text-3xl font-bold text-slate-900 dark:text-white">Sign in</h1>

            <p className="mt-2 text-slate-500">{APP_TAGLINE}</p>

          </div>



          <form onSubmit={handleSubmit} className="health-card space-y-4 shadow-xl shadow-slate-200/50 dark:shadow-none">

            {registered && (

              <p className="rounded-xl bg-emerald-50 px-3 py-2 text-sm text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300">

                Account created successfully. Please sign in to continue.

              </p>

            )}



            <div>

              <label className="text-sm font-medium text-slate-600 dark:text-slate-400">Email</label>

              <input

                type="email"

                required

                value={email}

                onChange={(e) => setEmail(e.target.value)}

                className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none focus:border-sky-400 dark:border-slate-600 dark:bg-slate-800"

                placeholder="you@example.com"

              />

            </div>



            <div>

              <label className="text-sm font-medium text-slate-600 dark:text-slate-400">Password</label>

              <input

                type="password"

                required

                minLength={6}

                value={password}

                onChange={(e) => setPassword(e.target.value)}

                className="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none focus:border-sky-400 dark:border-slate-600 dark:bg-slate-800"

                placeholder="••••••••"

              />

            </div>



            {error && (

              <p className="rounded-xl bg-red-50 px-3 py-2 text-sm text-red-600 dark:bg-red-950/50 dark:text-red-300">

                {error}

              </p>

            )}



            <button

              type="submit"

              disabled={loading}

              className="w-full rounded-xl bg-slate-900 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:opacity-60 dark:bg-sky-600 dark:hover:bg-sky-500"

            >

              {loading ? 'Signing in...' : 'Sign In'}

            </button>



            <p className="text-center text-sm text-slate-500">

              No account?{' '}

              <Link to="/register" className="font-medium text-sky-600 hover:text-sky-700 dark:text-sky-400">

                Create one

              </Link>

            </p>

            <p className="text-center text-xs text-slate-400">

              <Link to="/" className="hover:text-sky-600 dark:hover:text-sky-400">

                ← Back to home

              </Link>

            </p>

          </form>

        </div>

      </div>

    </div>

  )

}

