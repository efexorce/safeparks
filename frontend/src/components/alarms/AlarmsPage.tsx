import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { alarmApi } from '../../services/api'
import { Alarm, AlarmSeverity, AlarmStatus, AlarmType } from '../../types'
import { format } from 'date-fns'
import { tr } from 'date-fns/locale'
import clsx from 'clsx'

const severityColors: Record<AlarmSeverity, string> = {
  critical: 'bg-red-700/30 text-red-300 border-red-700/40',
  high: 'bg-red-500/20 text-red-400 border-red-500/30',
  medium: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  low: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
}

const alarmTypeLabels: Record<AlarmType, string> = {
  vandalism: 'Vandalizm',
  fight: 'Kavga',
  person_down: 'Yerde Kişi',
  suspicious_object: 'Şüpheli Nesne',
  intrusion: 'Yetkisiz Giriş',
  fire: 'Yangın',
  flood: 'Su Baskını',
  unknown: 'Bilinmeyen',
}

const statusLabels: Record<AlarmStatus, string> = {
  pending: 'Bekliyor',
  acknowledged: 'Onaylandı',
  investigating: 'İnceleniyor',
  resolved: 'Çözüldü',
  false_positive: 'Yanlış Alarm',
}

export default function AlarmsPage() {
  const [statusFilter, setStatusFilter] = useState<AlarmStatus | ''>('')
  const [page, setPage] = useState(1)
  const qc = useQueryClient()
  const DUMMY_USER = '00000000-0000-0000-0000-000000000001'

  const { data, isLoading } = useQuery(
    ['alarms', page, statusFilter],
    () => alarmApi.list({ page, page_size: 20, status: statusFilter || undefined }).then(r => r.data),
    { refetchInterval: 10000, keepPreviousData: true }
  )

  const acknowledgeMutation = useMutation(
    (id: string) => alarmApi.acknowledge(id, DUMMY_USER),
    { onSuccess: () => qc.invalidateQueries('alarms') }
  )

  const resolveMutation = useMutation(
    (id: string) => alarmApi.resolve(id, DUMMY_USER),
    { onSuccess: () => qc.invalidateQueries('alarms') }
  )

  const alarms: Alarm[] = data?.alarms ?? []
  const total: number = data?.total ?? 0

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <select
          className="bg-dark-800 border border-dark-700 text-white rounded-lg px-3 py-2 text-sm"
          value={statusFilter}
          onChange={e => { setStatusFilter(e.target.value as AlarmStatus | ''); setPage(1) }}
        >
          <option value="">Tüm Durumlar</option>
          {(Object.keys(statusLabels) as AlarmStatus[]).map(s => (
            <option key={s} value={s}>{statusLabels[s]}</option>
          ))}
        </select>
        <span className="text-slate-400 text-sm ml-auto">{total} alarm</span>
      </div>

      {isLoading ? (
        <div className="text-center py-20 text-slate-500">Yükleniyor...</div>
      ) : (
        <div className="space-y-3">
          {alarms.map(alarm => (
            <div key={alarm.id} className="bg-dark-800 border border-dark-700 rounded-xl p-4">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className={clsx('status-badge border text-xs', severityColors[alarm.severity])}>
                      {alarm.severity.toUpperCase()}
                    </span>
                    <span className="text-white font-semibold">{alarmTypeLabels[alarm.alarm_type]}</span>
                    <span className="text-slate-500 text-xs">{statusLabels[alarm.status]}</span>
                  </div>
                  {alarm.location_name && (
                    <p className="text-slate-400 text-sm mt-1">{alarm.location_name}</p>
                  )}
                  <p className="text-slate-500 text-xs mt-1">
                    {format(new Date(alarm.triggered_at), 'dd MMM yyyy HH:mm:ss', { locale: tr })}
                    {alarm.confidence_score && ` — Güven: %${(alarm.confidence_score * 100).toFixed(1)}`}
                    {alarm.detection_latency_ms && ` — Gecikme: ${alarm.detection_latency_ms.toFixed(0)}ms`}
                  </p>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  {alarm.status === 'pending' && (
                    <button
                      onClick={() => acknowledgeMutation.mutate(alarm.id)}
                      className="px-3 py-1.5 bg-yellow-600/20 border border-yellow-600/30 text-yellow-400 rounded-lg text-xs hover:bg-yellow-600/30 transition-colors"
                    >
                      Onayla
                    </button>
                  )}
                  {(alarm.status === 'pending' || alarm.status === 'acknowledged') && (
                    <button
                      onClick={() => resolveMutation.mutate(alarm.id)}
                      className="px-3 py-1.5 bg-green-600/20 border border-green-600/30 text-green-400 rounded-lg text-xs hover:bg-green-600/30 transition-colors"
                    >
                      Çöz
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
          {alarms.length === 0 && (
            <div className="text-center py-16 text-slate-500">Kayıt bulunamadı</div>
          )}
        </div>
      )}

      {total > 20 && (
        <div className="flex items-center justify-between pt-2">
          <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} className="px-3 py-1.5 bg-dark-700 text-slate-300 rounded-lg text-sm disabled:opacity-40">Önceki</button>
          <span className="text-slate-400 text-sm">Sayfa {page} / {Math.ceil(total / 20)}</span>
          <button onClick={() => setPage(p => p + 1)} disabled={page >= Math.ceil(total / 20)} className="px-3 py-1.5 bg-dark-700 text-slate-300 rounded-lg text-sm disabled:opacity-40">Sonraki</button>
        </div>
      )}
    </div>
  )
}
