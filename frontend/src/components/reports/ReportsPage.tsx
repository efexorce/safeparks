import React, { useState } from 'react'
import { useQuery } from 'react-query'
import { reportApi } from '../../services/api'
import { format } from 'date-fns'
import { tr } from 'date-fns/locale'

export default function ReportsPage() {
  const [reportType, setReportType] = useState<'daily' | 'monthly'>('daily')
  const [selectedDate, setSelectedDate] = useState(format(new Date(), 'yyyy-MM-dd'))
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear())
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1)

  const { data: dailyData, isLoading: dailyLoading } = useQuery(
    ['report-daily', selectedDate],
    () => reportApi.daily(selectedDate).then(r => r.data),
    { enabled: reportType === 'daily' }
  )

  const { data: monthlyData, isLoading: monthlyLoading } = useQuery(
    ['report-monthly', selectedYear, selectedMonth],
    () => reportApi.monthly(selectedYear, selectedMonth).then(r => r.data),
    { enabled: reportType === 'monthly' }
  )

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <div className="flex bg-dark-800 border border-dark-700 rounded-lg p-1">
          {(['daily', 'monthly'] as const).map(type => (
            <button
              key={type}
              onClick={() => setReportType(type)}
              className={`px-4 py-1.5 rounded-md text-sm transition-colors ${reportType === type ? 'bg-primary-600 text-white' : 'text-slate-400 hover:text-white'}`}
            >
              {type === 'daily' ? 'Günlük' : 'Aylık'}
            </button>
          ))}
        </div>

        {reportType === 'daily' ? (
          <input
            type="date"
            value={selectedDate}
            onChange={e => setSelectedDate(e.target.value)}
            className="bg-dark-800 border border-dark-700 text-white rounded-lg px-3 py-2 text-sm"
          />
        ) : (
          <div className="flex gap-2">
            <input type="number" value={selectedYear} min={2020} max={2030} onChange={e => setSelectedYear(+e.target.value)} className="bg-dark-800 border border-dark-700 text-white rounded-lg px-3 py-2 text-sm w-24" placeholder="Yıl" />
            <input type="number" value={selectedMonth} min={1} max={12} onChange={e => setSelectedMonth(+e.target.value)} className="bg-dark-800 border border-dark-700 text-white rounded-lg px-3 py-2 text-sm w-20" placeholder="Ay" />
          </div>
        )}
      </div>

      {reportType === 'daily' && (
        <div className="space-y-4">
          {dailyLoading ? (
            <div className="text-center py-16 text-slate-500">Rapor yükleniyor...</div>
          ) : dailyData ? (
            <>
              <h2 className="text-white font-semibold text-lg">{dailyData.date} Günlük Raporu</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-dark-800 border border-dark-700 rounded-xl p-5">
                  <h3 className="text-slate-400 text-sm mb-3">Alarm Özeti</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between"><span className="text-slate-400">Toplam Alarm</span><span className="text-white font-semibold">{dailyData.alarms.total}</span></div>
                    <div className="flex justify-between"><span className="text-slate-400">Çözülen</span><span className="text-green-400">{dailyData.alarms.resolved}</span></div>
                    <div className="flex justify-between"><span className="text-slate-400">Yanlış Alarm</span><span className="text-slate-400">{dailyData.alarms.false_positives}</span></div>
                  </div>
                </div>
                <div className="bg-dark-800 border border-dark-700 rounded-xl p-5">
                  <h3 className="text-slate-400 text-sm mb-3">Bant Genişliği</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between"><span className="text-slate-400">Toplam Kullanım</span><span className="text-blue-400 font-semibold">{dailyData.bandwidth.total_gb} GB</span></div>
                  </div>
                </div>
                <div className="bg-dark-800 border border-dark-700 rounded-xl p-5">
                  <h3 className="text-slate-400 text-sm mb-3">Enerji</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between"><span className="text-slate-400">Ort. Tüketim</span><span className="text-white">{dailyData.energy.avg_consumption_w} W</span></div>
                    <div className="flex justify-between"><span className="text-slate-400">Solar Üretim</span><span className="text-green-400">{dailyData.energy.total_solar_output_w} W</span></div>
                  </div>
                </div>
              </div>
            </>
          ) : null}
        </div>
      )}

      {reportType === 'monthly' && (
        <div className="space-y-4">
          {monthlyLoading ? (
            <div className="text-center py-16 text-slate-500">Rapor yükleniyor...</div>
          ) : monthlyData ? (
            <>
              <h2 className="text-white font-semibold text-lg">{monthlyData.year} - {monthlyData.month}. Ay Raporu</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-dark-800 border border-dark-700 rounded-xl p-5">
                  <h3 className="text-slate-400 text-sm mb-3">Kamera Durumu</h3>
                  <div className="text-sm"><div className="flex justify-between"><span className="text-slate-400">Aktif Kamera</span><span className="text-white font-semibold">{monthlyData.active_cameras}</span></div></div>
                </div>
                <div className="bg-dark-800 border border-dark-700 rounded-xl p-5">
                  <h3 className="text-slate-400 text-sm mb-3">Alarm Analizi</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between"><span className="text-slate-400">Toplam Alarm</span><span className="text-white font-semibold">{monthlyData.alarms.total}</span></div>
                    <div className="flex justify-between"><span className="text-slate-400">Yanlış Alarm Oranı</span><span className="text-yellow-400">%{monthlyData.alarms.false_positive_rate_percent}</span></div>
                  </div>
                </div>
              </div>
            </>
          ) : null}
        </div>
      )}
    </div>
  )
}
