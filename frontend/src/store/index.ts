import { create } from 'zustand'
import { Alarm, CameraStats, AlarmSummary, EnergyStats } from '../types'

interface AppState {
  pendingAlarms: Alarm[]
  cameraStats: CameraStats | null
  alarmSummary: AlarmSummary | null
  energyStats: EnergyStats | null
  selectedCameraId: string | null
  sidebarOpen: boolean
  addPendingAlarm: (alarm: Alarm) => void
  removePendingAlarm: (id: string) => void
  setCameraStats: (stats: CameraStats) => void
  setAlarmSummary: (summary: AlarmSummary) => void
  setEnergyStats: (stats: EnergyStats) => void
  setSelectedCamera: (id: string | null) => void
  toggleSidebar: () => void
}

export const useAppStore = create<AppState>((set) => ({
  pendingAlarms: [],
  cameraStats: null,
  alarmSummary: null,
  energyStats: null,
  selectedCameraId: null,
  sidebarOpen: true,

  addPendingAlarm: (alarm) =>
    set((state) => ({
      pendingAlarms: [alarm, ...state.pendingAlarms].slice(0, 100),
    })),

  removePendingAlarm: (id) =>
    set((state) => ({
      pendingAlarms: state.pendingAlarms.filter((a) => a.id !== id),
    })),

  setCameraStats: (stats) => set({ cameraStats: stats }),
  setAlarmSummary: (summary) => set({ alarmSummary: summary }),
  setEnergyStats: (stats) => set({ energyStats: stats }),
  setSelectedCamera: (id) => set({ selectedCameraId: id }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
}))
