import { useEffect, useRef, useCallback } from 'react'
import { WebSocketMessage } from '../types'

export function useWebSocket(
  onMessage: (msg: WebSocketMessage) => void,
  enabled: boolean = true
) {
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const onMessageRef = useRef(onMessage)
  onMessageRef.current = onMessage

  const connect = useCallback(() => {
    if (!enabled) return
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const url = `${protocol}//${window.location.host}/ws/alerts`
    const ws = new WebSocket(url)

    ws.onopen = () => {
      console.log('WebSocket connected')
    }

    ws.onmessage = (event) => {
      try {
        const msg: WebSocketMessage = JSON.parse(event.data)
        onMessageRef.current(msg)
      } catch {
        // ignore malformed messages
      }
    }

    ws.onclose = () => {
      if (enabled) {
        reconnectTimerRef.current = setTimeout(connect, 3000)
      }
    }

    ws.onerror = () => {
      ws.close()
    }

    const pingInterval = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send('ping')
      }
    }, 30000)

    ws.addEventListener('close', () => clearInterval(pingInterval))
    wsRef.current = ws
  }, [enabled])

  useEffect(() => {
    connect()
    return () => {
      if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current)
      wsRef.current?.close()
    }
  }, [connect])
}
