import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/dashboard/Layout'
import DashboardHome from './components/dashboard/DashboardHome'
import CamerasPage from './components/cameras/CamerasPage'
import AlarmsPage from './components/alarms/AlarmsPage'
import EnergyPage from './components/energy/EnergyPage'
import ReportsPage from './components/reports/ReportsPage'
import MapPage from './components/map/MapPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardHome />} />
          <Route path="cameras" element={<CamerasPage />} />
          <Route path="alarms" element={<AlarmsPage />} />
          <Route path="energy" element={<EnergyPage />} />
          <Route path="reports" element={<ReportsPage />} />
          <Route path="map" element={<MapPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
