import React, { useState } from 'react'
import { useQuery } from 'react-query'
import { cameraApi } from '../../services/api'
import { Camera, CameraStatus } from '../../types'
import clsx from 'clsx'

const statusColors: Record<CameraStatus, string> = {
  online: 'bg-green-500/20 text-green-400 border-green-500/30',
  offline: 'bg-red-500/20 text-red-400 border-red-500/30',
  sleep: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  maintenance: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  error: 'bg-red-700/20 text-red-300 border-red-700/30',
}

const statusLabels: Record<CameraStatus, string> = {
  online: 'Aktif',
  offline: 'Çevrimdışı',
  sleep: 'Uyku',
  maintenance: 'Bakım',
  error: 'Hata',
}

export default function CamerasPage() {
  const [statusFilter, setStatusFilter] = useState<CameraStatus | ''>('')
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)

  const { data, isLoading } = useQuery(
    ['cameras', page, statusFilter],
    () => cameraApi.list({ page, page_size: 20, status: statusFilter || undefined }).then(r => r.data),
    { keepPreviousData: true }
  )

  const cameras: Camera[] = data?.cameras ?? []
  const total: number = data?.total ?? 0

  const filtered = search
    ? cameras.filter(c => c.name.toLowerCase().includes(search.toLowerCase()) || c.location_name.toLowerCase().includes(search.toLowerCase()))
    : cameras

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <input
          className="bg-dark-800 border border-dark-700 text-white placeholder-slate-500 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-primary-500 w-60"
          placeholder="Kamera veya konum ara..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <select
          className="bg-dark-800 border border-dark-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-primary-500"
          value={statusFilter}
          onChange={e => { setStatusFilter(e.target.value as CameraStatus | ''); setPage(1) }}
        >
          <option value="">Tüm Durumlar</option>
          {(Object.keys(statusLabels) as CameraStatus[]).map(s => (
            <option key={s} value={s}>{statusLabels[s]}</option>
          ))}
        </select>
        <span className="text-slate-400 text-sm ml-auto">{total} kamera</span>
      </div>

      {isLoading ? (
        <div className="text-center py-20 text-slate-500">Yükleniyor...</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-slate-400 border-b border-dark-700 text-left">
                <th className="pb-3 pr-4">Kamera</th>
                <th className="pb-3 pr-4">Konum</th>
                <th className="pb-3 pr-4">Durum</th>
                <th className="pb-3 pr-4">AI</th>
                <th className="pb-3 pr-4">Çözünürlük</th>
                <th className="pb-3 pr-4">FPS</th>
                <th className="pb-3 pr-4">Günlük Veri</th>
                <th className="pb-3">Hareket</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-dark-700">
              {filtered.map(cam => (
                <tr key={cam.id} className="hover:bg-dark-800/50 transition-colors">
                  <td className="py-3 pr-4">
                    <div className="text-white font-medium">{cam.name}</div>
                    <div className="text-slate-500 text-xs">{cam.district}</div>
                  </td>
                  <td className="py-3 pr-4 text-slate-300 max-w-xs truncate">{cam.location_name}</td>
                  <td className="py-3 pr-4">
                    <span className={clsx('status-badge border', statusColors[cam.status])}>
                      {statusLabels[cam.status]}
                    </span>
                  </td>
                  <td className="py-3 pr-4">
                    <span className={clsx('status-badge border', cam.ai_status === 'active' ? 'bg-blue-500/20 text-blue-400 border-blue-500/30' : 'bg-dark-700 text-slate-500 border-dark-600')}>
                      {cam.ai_status === 'active' ? 'Aktif' : 'Uyku'}
                    </span>
                  </td>
                  <td className="py-3 pr-4 text-slate-300">{cam.current_resolution}</td>
                  <td className="py-3 pr-4 text-slate-300">{cam.current_fps}</td>
                  <td className="py-3 pr-4 text-slate-300">{cam.daily_data_used_gb.toFixed(2)} GB</td>
                  <td className="py-3">
                    <span className={clsx('w-2 h-2 rounded-full inline-block', cam.motion_detected ? 'bg-orange-400 animate-pulse' : 'bg-dark-600')} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {total > 20 && (
        <div className="flex items-center justify-between pt-2">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-3 py-1.5 bg-dark-700 text-slate-300 rounded-lg text-sm disabled:opacity-40"
          >
            Önceki
          </button>
          <span className="text-slate-400 text-sm">Sayfa {page} / {Math.ceil(total / 20)}</span>
          <button
            onClick={() => setPage(p => p + 1)}
            disabled={page >= Math.ceil(total / 20)}
            className="px-3 py-1.5 bg-dark-700 text-slate-300 rounded-lg text-sm disabled:opacity-40"
          >
            Sonraki
          </button>
        </div>
      )}
    </div>
  )
}
