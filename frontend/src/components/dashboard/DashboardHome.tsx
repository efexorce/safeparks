import React from 'react'
import { useQuery } from 'react-query'
import { cameraApi, alarmApi, energyApi } from '../../services/api'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

function StatCard({ title, value, sub, color = 'blue' }: { title: string; value: string | number; sub?: string; color?: string }) {
  const colors: Record<string, string> = {
    blue: 'border-blue-500/30 bg-blue-900/10',
    green: 'border-green-500/30 bg-green-900/10',
    red: 'border-red-500/30 bg-red-900/10',
    yellow: 'border-yellow-500/30 bg-yellow-900/10',
    purple: 'border-purple-500/30 bg-purple-900/10',
  }
  return (
    <div className={`border rounded-xl p-5 ${colors[color] || colors.blue}`}>
      <p className="text-slate-400 text-xs mb-1">{title}</p>
      <p className="text-white text-2xl font-bold">{value}</p>
      {sub && <p className="text-slate-500 text-xs mt-1">{sub}</p>}
    </div>
  )
}

export default function DashboardHome() {
  const { data: camStats } = useQuery('cameraStats', () => cameraApi.stats().then(r => r.data), { refetchInterval: 15000 })
  const { data: alarmSum } = useQuery('alarmSummary', () => alarmApi.summary().then(r => r.data), { refetchInterval: 15000 })
  const { data: energy } = useQuery('energyStats', () => energyApi.cityStats().then(r => r.data), { refetchInterval: 30000 })

  const pieData = camStats ? [
    { name: 'Aktif', value: camStats.online_cameras, color: '#22c55e' },
    { name: 'Uyku', value: camStats.sleep_cameras, color: '#f59e0b' },
    { name: 'Çevrimdışı', value: camStats.offline_cameras, color: '#ef4444' },
  ] : []

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-4 xl:grid-cols-6 gap-4">
        <StatCard title="Toplam Kamera" value={camStats?.total_cameras ?? '-'} color="blue" />
        <StatCard title="Aktif Kamera" value={camStats?.online_cameras ?? '-'} color="green" />
        <StatCard title="Uyku Modu" value={camStats?.sleep_cameras ?? '-'} sub="Enerji tasarrufu" color="yellow" />
        <StatCard title="Bekleyen Alarm" value={alarmSum?.pending ?? '-'} color="red" />
        <StatCard title="Enerji Tüketimi" value={energy ? `${energy.total_consumption_kw} kW` : '-'} color="purple" />
        <StatCard title="Güneş Enerjisi" value={energy ? `%${energy.solar_ratio_percent}` : '-'} sub="Solar katkı" color="green" />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-2 bg-dark-800 border border-dark-700 rounded-xl p-5">
          <h3 className="text-white font-semibold mb-4">5G Bant Genişliği Kullanımı</h3>
          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-xs text-slate-400 mb-1">
                <span>Günlük Kullanım</span>
                <span>{camStats?.total_daily_data_gb?.toFixed(1) ?? 0} / {((camStats?.total_cameras ?? 0) * 13.5).toFixed(0)} GB</span>
              </div>
              <div className="w-full bg-dark-700 rounded-full h-2">
                <div
                  className="bg-blue-500 h-2 rounded-full transition-all"
                  style={{ width: `${Math.min(100, ((camStats?.total_daily_data_gb ?? 0) / Math.max((camStats?.total_cameras ?? 1) * 13.5, 1)) * 100)}%` }}
                />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-xs text-slate-400 mb-1">
                <span>Aylık Kullanım</span>
                <span>{camStats?.total_monthly_data_gb?.toFixed(0) ?? 0} / {((camStats?.total_cameras ?? 0) * 400).toFixed(0)} GB</span>
              </div>
              <div className="w-full bg-dark-700 rounded-full h-2">
                <div
                  className="bg-purple-500 h-2 rounded-full transition-all"
                  style={{ width: `${Math.min(100, ((camStats?.total_monthly_data_gb ?? 0) / Math.max((camStats?.total_cameras ?? 1) * 400, 1)) * 100)}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        <div className="bg-dark-800 border border-dark-700 rounded-xl p-5">
          <h3 className="text-white font-semibold mb-4">Kamera Durumu</h3>
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={160}>
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={45} outerRadius={70} dataKey="value">
                  {pieData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', color: '#e2e8f0', fontSize: '12px' }} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-40 flex items-center justify-center text-slate-500 text-sm">Veri yükleniyor...</div>
          )}
          <div className="flex justify-center gap-4 mt-2">
            {pieData.map(d => (
              <div key={d.name} className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: d.color }} />
                <span className="text-xs text-slate-400">{d.name} ({d.value})</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <div className="bg-dark-800 border border-dark-700 rounded-xl p-5">
          <h3 className="text-white font-semibold mb-2">Enerji Durumu</h3>
          <div className="space-y-2 mt-3">
            <div className="flex justify-between text-sm">
              <span className="text-slate-400">Toplam Tüketim</span>
              <span className="text-white">{energy?.total_consumption_kw ?? 0} kW</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-slate-400">Solar Çıkışı</span>
              <span className="text-green-400">{energy?.total_solar_output_kw ?? 0} kW</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-slate-400">Tasarruf Edilen Enerji</span>
              <span className="text-yellow-400">{energy?.energy_saved_kwh ?? 0} kWh</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-slate-400">Uyku Modundaki Kamera</span>
              <span className="text-blue-400">{energy?.cameras_in_sleep ?? 0} / {energy?.total_cameras ?? 0}</span>
            </div>
          </div>
        </div>

        <div className="bg-dark-800 border border-dark-700 rounded-xl p-5">
          <h3 className="text-white font-semibold mb-2">Alarm Özeti</h3>
          <div className="space-y-2 mt-3">
            {[
              { label: 'Bekleyen', value: alarmSum?.pending ?? 0, color: 'text-red-400' },
              { label: 'Onaylandı', value: alarmSum?.acknowledged ?? 0, color: 'text-yellow-400' },
              { label: 'Çözüldü', value: alarmSum?.resolved ?? 0, color: 'text-green-400' },
              { label: 'Yanlış Alarm', value: alarmSum?.false_positives ?? 0, color: 'text-slate-400' },
              { label: 'Toplam', value: alarmSum?.total ?? 0, color: 'text-white' },
            ].map(item => (
              <div key={item.label} className="flex justify-between text-sm">
                <span className="text-slate-400">{item.label}</span>
                <span className={item.color + ' font-semibold'}>{item.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
