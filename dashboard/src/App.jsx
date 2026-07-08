import { Navigate, Route, Routes } from 'react-router-dom'

import GuestRoute from './components/GuestRoute'

import ProtectedRoute from './components/ProtectedRoute'

import { AuthProvider } from './context/AuthContext'

import { ThemeProvider } from './context/ThemeContext'

import Dashboard from './pages/Dashboard'

import HomePage from './pages/HomePage'

import LoginPage from './pages/Login'

import RegisterPage from './pages/Register'



function App() {

  return (

    <ThemeProvider>

      <AuthProvider>

        <Routes>

          <Route path="/" element={<HomePage />} />

          <Route

            path="/login"

            element={

              <GuestRoute>

                <LoginPage />

              </GuestRoute>

            }

          />

          <Route

            path="/register"

            element={

              <GuestRoute>

                <RegisterPage />

              </GuestRoute>

            }

          />

          <Route

            path="/dashboard/*"

            element={

              <ProtectedRoute>

                <Dashboard />

              </ProtectedRoute>

            }

          />

          <Route path="*" element={<Navigate to="/" replace />} />

        </Routes>

      </AuthProvider>

    </ThemeProvider>

  )

}



export default App

