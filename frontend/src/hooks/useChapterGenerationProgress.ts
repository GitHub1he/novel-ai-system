import { useState, useEffect, useRef } from 'react'
import { message } from 'antd'

interface ProgressMessage {
  type: 'progress' | 'version_complete' | 'all_complete' | 'error'
  data?: any
}

interface GenerationProgress {
  currentVersion: number
  totalVersions: number
  status: string
  versions: any[]
}

export const useChapterGenerationProgress = (taskId: string | null) => {
  const [progress, setProgress] = useState<GenerationProgress>({
    currentVersion: 0,
    totalVersions: 0,
    status: '',
    versions: []
  })
  const [isConnected, setIsConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    if (!taskId) return

    // 构建 WebSocket URL
    const wsUrl = `ws://localhost:8000/ws/chapters/generate/${taskId}`
    const ws = new WebSocket(wsUrl)
    wsRef.current = ws

    ws.onopen = () => {
      console.log('WebSocket 连接已建立')
      setIsConnected(true)
    }

    ws.onmessage = (event) => {
      try {
        const message: ProgressMessage = JSON.parse(event.data)

        switch (message.type) {
          case 'progress':
            setProgress(prev => ({
              ...prev,
              currentVersion: message.data.current_version,
              totalVersions: message.data.total_versions,
              status: message.data.status
            }))
            break

          case 'version_complete':
            setProgress(prev => ({
              ...prev,
              versions: [...prev.versions, message.data.version]
            }))
            message.success(`✨ 版本 ${message.data.version_number || prev.versions.length + 1} 生成完成`)
            break

          case 'all_complete':
            setProgress(prev => ({
              ...prev,
              status: '完成'
            }))
            message.success('🎉 所有版本生成完成！')
            break

          case 'error':
            message.error(`❌ 生成失败: ${message.data.error}`)
            break

          default:
            console.log('未知消息类型:', message)
        }
      } catch (error) {
        console.error('解析 WebSocket 消息失败:', error)
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket 错误:', error)
      message.error('WebSocket 连接错误')
    }

    ws.onclose = () => {
      console.log('WebSocket 连接已关闭')
      setIsConnected(false)
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }
    }
  }, [taskId])

  const resetProgress = () => {
    setProgress({
      currentVersion: 0,
      totalVersions: 0,
      status: '',
      versions: []
    })
  }

  return {
    progress,
    isConnected,
    resetProgress
  }
}
