import React, { useEffect, useState } from 'react'
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet'
import { useQuery } from 'react-query'
import { cameraApi } from '../../services/api'
import { MapCamera } from '../../types'

const STATUS_COLORS: Record<string, string> = {
  online: '#22c55e',
  offline: '#ef4444',
  sleep: '#f59e0b',
  maintenance: '#3b82f6',
  error: '#dc2626',
}

function MapBounds({ cameras }: { cameras: MapCamera[] }) {
  const map = useMap()
  useEffect(() => {
    if (cameras.length > 0) {
      const lats = cameras.map(c => c.latitude)
      const lngs = cameras.map(c => c.longitude)
      const bounds: [[number, number], [number, number]] = [
        [Math.min(...lats), Math.min(...lngs)],
        [Math.max(...lats), Math.max(...lngs)],
      ]
      if (Math.abs(bounds[0][0] - bounds[1][0]) > 0.001 || Math.abs(bounds[0][1] - bounds[1][1]) > 0.001) {
        map.fitBounds(bounds, { padding: [40, 40] })
      }
    }
  }, [cameras, map])
  return null
}

export default function MapPage() {
  const [selectedStatus, setSelectedStatus] = useState<string>('')

  const { data: cameras = [], isLoading } = useQuery(
    'cameraMap',
    () => cameraApi.mapData().then(r => r.data),
    { refetchInterval: 15000 }
  )

  const filtered: MapCamera[] = selectedStatus
    ? cameras.filter((c: MapCamera) => c.status === selectedStatus)
    : cameras

  const stats = {
    online: cameras.filter((c: MapCamera) => c.status === 'online').length,
    sleep: cameras.filter((c: MapCamera) => c.status === 'sleep').length,
    offline: cameras.filter((c: MapCamera) => c.status === 'offline').length,
  }

  return (
    <div className="space-y-4 h-full flex flex-col">
      <div className="flex items-center gap-3 flex-wrap flex-shrink-0">
        <button onClick={() => setSelectedStatus('')} className={`px-3 py-1.5 rounded-lg text-sm border transition-colors ${!selectedStatus ? 'bg-primary-600 border-primary-500 text-white' : 'bg-dark-800 border-dark-700 text-slate-400 hover:text-white'}`}>
          Tümü ({cameras.length})
        </button>
        {Object.entries({ online: `Aktif (${stats.online})`, sleep: `Uyku (${stats.sleep})`, offline: `Çevrimdışı (${stats.offline})` }).map(([status, label]) => (
          <button key={status} onClick={() => setSelectedStatus(status)} className={`px-3 py-1.5 rounded-lg text-sm border transition-colors ${selectedStatus === status ? 'bg-primary-600 border-primary-500 text-white' : 'bg-dark-800 border-dark-700 text-slate-400 hover:text-white'}`}>
            {label}
          </button>
        ))}
      </div>

      <div className="flex-1 min-h-96 rounded-xl overflow-hidden border border-dark-700">
        {isLoading ? (
          <div className="h-full flex items-center justify-center bg-dark-800 text-slate-500">Harita yükleniyor...</div>
        ) : (
          <MapContainer center={[39.9334, 32.8597]} zoom={10} style={{ height: '100%', width: '100%', background: '#1e293b' }}>
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            />
            <MapBounds cameras={filtered} />
            {filtered.map((cam: MapCamera) => (
              <CircleMarker
                key={cam.id}
                center={[cam.latitude, cam.longitude]}
                radius={cam.motion_detected ? 10 : 7}
                pathOptions={{
                  color: STATUS_COLORS[cam.status] || '#6b7280',
                  fillColor: STATUS_COLORS[cam.status] || '#6b7280',
                  fillOpacity: 0.85,
                  weight: cam.motion_detected ? 2 : 1,
                }}
              >
                <Popup className="safeparks-popup">
                  <div style={{ background: '#1e293b', color: '#e2e8f0', padding: '8px', borderRadius: '8px', minWidth: '180px', fontSize: '12px' }}>
                    <p style={{ fontWeight: 600, marginBottom: 4 }}>{cam.name}</p>
                    <p style={{ color: '#94a3b8', marginBottom: 2 }}>{cam.park_zone || cam.district}</p>
                    <div style={{ display: 'flex', gap: 8, marginTop: 4 }}>
                      <span style={{ color: STATUS_COLORS[cam.status] }}>● {cam.status}</span>
                      {cam.motion_detected && <span style={{ color: '#f97316' }}>Hareket!</span>}
                    </div>
                    <p style={{ color: '#64748b', marginTop: 4 }}>{cam.current_resolution} · {cam.daily_data_used_gb.toFixed(2)}GB/gün</p>
                  </div>
                </Popup>
              </CircleMarker>
            ))}
          </MapContainer>
        )}
      </div>
    </div>
  )
}
