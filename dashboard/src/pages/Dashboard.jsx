import { Routes, Route, Navigate } from 'react-router-dom'
import DashboardLayout from '../components/DashboardLayout'
import { DashboardProvider } from '../context/DashboardContext'
import OverviewPage from './OverviewPage'
import WeeklyPage from './WeeklyPage'
import InsightsPage from './InsightsPage'
import ProfilePage from './ProfilePage'

export default function Dashboard() {
  return (
    <DashboardProvider>
      <Routes>
        <Route element={<DashboardLayout />}>
          <Route index element={<OverviewPage />} />
          <Route path="weekly" element={<WeeklyPage />} />
          <Route path="insights" element={<InsightsPage />} />
          <Route path="profile" element={<ProfilePage />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Route>
      </Routes>
    </DashboardProvider>
  )
}
