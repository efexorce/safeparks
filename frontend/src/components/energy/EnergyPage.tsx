import React from 'react'
import { useQuery } from 'react-query'
import { energyApi } from '../../services/api'
import { RadialBarChart, RadialBar, ResponsiveContainer, Tooltip } from 'recharts'

export default function EnergyPage() {
  const { data: stats, isLoading } = useQuery('energyStats', () => energyApi.cityStats().then(r => r.data), { refetchInterval: 30000 })
  const { data: panels } = useQuery('solarPanels', () => energyApi.solarPanels().then(r => r.data))

  const solarData = stats ? [{ name: 'Solar', value: stats.solar_ratio_percent, fill: '#22c55e' }] : []

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          { label: 'Toplam Tüketim', value: stats ? `${stats.total_consumption_kw} kW` : '-', sub: 'Anlık şehir toplamı', color: 'text-blue-400' },
          { label: 'Solar Üretim', value: stats ? `${stats.total_solar_output_kw} kW` : '-', sub: `%${stats?.solar_ratio_percent ?? 0} katkı`, color: 'text-green-400' },
          { label: 'Enerji Tasarrufu', value: stats ? `${stats.energy_saved_kwh} kWh` : '-', sub: stats?.cost_saved_usd ? `$${stats.cost_saved_usd} tasarruf` : 'Uyku modu sayesinde', color: 'text-yellow-400' },
        ].map(card => (
          <div key={card.label} className="bg-dark-800 border border-dark-700 rounded-xl p-5">
            <p className="text-slate-400 text-xs mb-1">{card.label}</p>
            <p className={`text-2xl font-bold ${card.color}`}>{card.value}</p>
            <p className="text-slate-500 text-xs mt-1">{card.sub}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <div className="bg-dark-800 border border-dark-700 rounded-xl p-5">
          <h3 className="text-white font-semibold mb-4">Solar Enerji Oranı</h3>
          {stats ? (
            <>
              <div className="flex items-center justify-center h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <RadialBarChart cx="50%" cy="50%" innerRadius="60%" outerRadius="80%" data={[{ name: 'Solar', value: stats.solar_ratio_percent, fill: '#22c55e' }, { name: 'Grid', value: 100 - stats.solar_ratio_percent, fill: '#334155' }]} startAngle={90} endAngle={-270}>
                    <RadialBar dataKey="value" />
                    <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', color: '#e2e8f0', fontSize: '12px', borderRadius: '8px' }} />
                  </RadialBarChart>
                </ResponsiveContainer>
              </div>
              <div className="text-center mt-2">
                <p className="text-3xl font-bold text-green-400">%{stats.solar_ratio_percent}</p>
                <p className="text-slate-400 text-sm">Güneş Enerjisi Katkısı</p>
              </div>
            </>
          ) : (
            <div className="h-48 flex items-center justify-center text-slate-500">Yükleniyor...</div>
          )}
        </div>

        <div className="bg-dark-800 border border-dark-700 rounded-xl p-5">
          <h3 className="text-white font-semibold mb-4">Kamera Enerji Modu</h3>
          {stats && (
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-xs text-slate-400 mb-1">
                  <span>Uyku Modundaki Kameralar</span>
                  <span>{stats.cameras_in_sleep} / {stats.total_cameras}</span>
                </div>
                <div className="w-full bg-dark-700 rounded-full h-3">
                  <div
                    className="bg-yellow-500 h-3 rounded-full"
                    style={{ width: `${stats.total_cameras > 0 ? (stats.cameras_in_sleep / stats.total_cameras) * 100 : 0}%` }}
                  />
                </div>
              </div>
              <div className="text-sm text-slate-400 space-y-2 mt-4">
                <div className="flex justify-between"><span>Aktif kamera güç tüketimi</span><span className="text-white">~15W / kamera</span></div>
                <div className="flex justify-between"><span>Uyku modu güç tüketimi</span><span className="text-yellow-400">~5W / kamera</span></div>
                <div className="flex justify-between"><span>Enerji tasarruf oranı</span><span className="text-green-400">%40-60</span></div>
                <div className="flex justify-between"><span>PoE desteği</span><span className="text-blue-400">Aktif</span></div>
              </div>
            </div>
          )}
        </div>
      </div>

      {panels && panels.length > 0 && (
        <div className="bg-dark-800 border border-dark-700 rounded-xl p-5">
          <h3 className="text-white font-semibold mb-4">Solar Panel Listesi ({panels.length})</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-slate-400 border-b border-dark-700 text-left">
                  <th className="pb-2 pr-4">Ad</th>
                  <th className="pb-2 pr-4">Kapasite</th>
                  <th className="pb-2 pr-4">Anlık Çıkış</th>
                  <th className="pb-2 pr-4">Batarya</th>
                  <th className="pb-2">Durum</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-dark-700">
                {panels.map((panel: any) => (
                  <tr key={panel.id} className="hover:bg-dark-700/30">
                    <td className="py-2 pr-4 text-white">{panel.name}</td>
                    <td className="py-2 pr-4 text-slate-300">{panel.capacity_watts}W</td>
                    <td className="py-2 pr-4 text-green-400">{panel.current_output_watts}W</td>
                    <td className="py-2 pr-4 text-slate-300">{panel.battery_level_percent?.toFixed(0)}%</td>
                    <td className="py-2">
                      <span className={clsx('status-badge border', panel.is_active ? 'bg-green-500/20 text-green-400 border-green-500/30' : 'bg-red-500/20 text-red-400 border-red-500/30')}>
                        {panel.is_active ? 'Aktif' : 'Kapalı'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

import clsx from 'clsx'
