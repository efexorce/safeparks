import React, { useEffect } from 'react'
import { Outlet, NavLink } from 'react-router-dom'
import { useQuery } from 'react-query'
import { cameraApi, alarmApi, energyApi } from '../../services/api'
import { useAppStore } from '../../store'
import { useWebSocket } from '../../hooks/useWebSocket'
import { WebSocketMessage, Alarm } from '../../types'
import clsx from 'clsx'

const navItems = [
  { to: '/dashboard', label: 'Genel Bakış', icon: '⬡' },
  { to: '/map', label: 'Harita', icon: '◉' },
  { to: '/cameras', label: 'Kameralar', icon: '◈' },
  { to: '/alarms', label: 'Alarmlar', icon: '◆' },
  { to: '/energy', label: 'Enerji', icon: '◇' },
  { to: '/reports', label: 'Raporlar', icon: '◻' },
]

export default function Layout() {
  const { setCameraStats, setAlarmSummary, setEnergyStats, addPendingAlarm, pendingAlarms, sidebarOpen, toggleSidebar } = useAppStore()

  const { data: cameraStats } = useQuery('cameraStats', () => cameraApi.stats().then(r => r.data), { refetchInterval: 15000 })
  const { data: alarmSummary } = useQuery('alarmSummary', () => alarmApi.summary().then(r => r.data), { refetchInterval: 15000 })
  const { data: energyStats } = useQuery('energyStats', () => energyApi.cityStats().then(r => r.data), { refetchInterval: 30000 })

  useEffect(() => { if (cameraStats) setCameraStats(cameraStats) }, [cameraStats, setCameraStats])
  useEffect(() => { if (alarmSummary) setAlarmSummary(alarmSummary) }, [alarmSummary, setAlarmSummary])
  useEffect(() => { if (energyStats) setEnergyStats(energyStats) }, [energyStats, setEnergyStats])

  useWebSocket((msg: WebSocketMessage) => {
    if (msg.type === 'alarm') {
      addPendingAlarm(msg.data as unknown as Alarm)
    }
  })

  return (
    <div className="flex h-screen bg-dark-900 overflow-hidden">
      <aside className={clsx('flex flex-col bg-dark-800 border-r border-dark-700 transition-all duration-300', sidebarOpen ? 'w-56' : 'w-16')}>
        <div className="flex items-center gap-3 px-4 py-5 border-b border-dark-700">
          <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center text-white font-bold text-sm flex-shrink-0">SP</div>
          {sidebarOpen && <span className="text-white font-semibold text-sm leading-tight">SafeParks</span>}
        </div>
        <nav className="flex-1 py-4 space-y-1 px-2">
          {navItems.map(item => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => clsx(
                'flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors',
                isActive ? 'bg-primary-600 text-white' : 'text-slate-400 hover:text-white hover:bg-dark-700'
              )}
            >
              <span className="text-base flex-shrink-0">{item.icon}</span>
              {sidebarOpen && <span>{item.label}</span>}
            </NavLink>
          ))}
        </nav>
        <div className="p-2 border-t border-dark-700">
          <button onClick={toggleSidebar} className="w-full flex items-center justify-center py-2 text-slate-500 hover:text-white text-xs">
            {sidebarOpen ? '«' : '»'}
          </button>
        </div>
      </aside>

      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="bg-dark-800 border-b border-dark-700 px-6 py-3 flex items-center justify-between flex-shrink-0">
          <h1 className="text-white font-semibold text-base">Akıllı Park Güvenlik ve İzleme Sistemi</h1>
          <div className="flex items-center gap-4">
            {pendingAlarms.length > 0 && (
              <div className="flex items-center gap-2 bg-red-900/40 border border-red-700 rounded-lg px-3 py-1">
                <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
                <span className="text-red-400 text-xs font-medium">{pendingAlarms.length} aktif alarm</span>
              </div>
            )}
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
              <span className="text-slate-400 text-xs">{cameraStats?.online_cameras ?? 0} kamera aktif</span>
            </div>
          </div>
        </header>
        <main className="flex-1 overflow-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
