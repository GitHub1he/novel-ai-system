import { useEffect, useState, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Layout, List, Button, Input, Card, Empty, Spin, Tabs, Space, Modal, message, Select, Popconfirm, Progress, Dropdown, Menu, Checkbox, Tag } from 'antd'
const { TextArea } = Input
import {
  BulbOutlined,
  TeamOutlined,
  GlobalOutlined,
  BookOutlined,
  PlusOutlined,
  EditOutlined,
  ArrowLeftOutlined,
  DeleteOutlined,
  ThunderboltOutlined,
  MoreOutlined,
  DownOutlined,
  SearchOutlined,
  ScanOutlined,
} from '@ant-design/icons'
import { projectApi, chapterApi, detectEntitiesFromChapter, createEntities } from '../services/api'
import CharacterManagement from '../components/CharacterManagement'
import WorldSettingManagement from '../components/WorldSettingManagement'
import ProjectStyleSettings from '../components/ProjectStyleSettings'
import ContextAnalysisView from '../components/ContextAnalysisView'
import ImprovedContextAnalysis from '../components/ImprovedContextAnalysis'
import AdvancedChapterGenerate from '../components/AdvancedChapterGenerate'
import VersionPreview from '../components/VersionPreview'
import SmartTextEditor from '../components/SmartTextEditor'
import type { Project, Chapter, Character, WorldSetting, ChapterGenerateRequest } from '../types'

const { Content, Sider } = Layout

const CHAPTER_STATUS_OPTIONS = [
  { label: '草稿', value: 'draft' },
  { label: '修订中', value: 'revising' },
  { label: '已完成', value: 'completed' },
]

const PROJECT_STATUS_CONFIG = {
  draft: { color: '#8c8c8c', label: '草稿' },
  revising: { color: '#1890ff', label: '修订中' },
  completed: { color: '#52c41a', label: '已完成' },
}

const ProjectDetail = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [project, setProject] = useState<Project | null>(null)
  const [chapters, setChapters] = useState<Chapter[]>([])
  const [currentChapter, setCurrentChapter] = useState<Chapter | null>(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [generatingModalVisible, setGeneratingModalVisible] = useState(false)
  const [generatingMessage, setGeneratingMessage] = useState('')
  const [generatingProgress, setGeneratingProgress] = useState(0)
  const generatingMessageInterval = useRef<NodeJS.Timeout | null>(null)
  const generatingProgressInterval = useRef<NodeJS.Timeout | null>(null)
  const [activeTab, setActiveTab] = useState('chapters')
  const [createModalVisible, setCreateModalVisible] = useState(false)
  const [newChapterTitle, setNewChapterTitle] = useState('')
  const [newChapterNumber, setNewChapterNumber] = useState(1)
  const [creating, setCreating] = useState(false)
  const [outlineModalVisible, setOutlineModalVisible] = useState(false)
  const [outlineContent, setOutlineContent] = useState('')
  const [saving, setSaving] = useState(false)
  const [loadingChapter, setLoadingChapter] = useState(false)
  const [styleSettingsVisible, setStyleSettingsVisible] = useState(false)
  const [contextAnalysisVisible, setContextAnalysisVisible] = useState(false)
  const [plotDirection, setPlotDirection] = useState('')

  // 高级生成相关状态
  const [advancedGenerateVisible, setAdvancedGenerateVisible] = useState(false)
  const [versionPreviewVisible, setVersionPreviewVisible] = useState(false)
  const [generatedVersions, setGeneratedVersions] = useState<any[]>([])
  const [currentChapterId, setCurrentChapterId] = useState<number | null>(null) // 当前生成版本的章节ID
  const [contextUsed, setContextUsed] = useState<any>(null)
  const [advancedGenerating, setAdvancedGenerating] = useState(false)
  const [selectedContextFromAnalysis, setSelectedContextFromAnalysis] = useState<any>(null) // 保存上下文分析的选择

  // 人物和世界观数据
  const [characters, setCharacters] = useState<Character[]>([])
  const [worldSettings, setWorldSettings] = useState<WorldSetting[]>([])

  // AI 文本编辑相关状态
  const [aiEditing, setAiEditing] = useState(false)
  const [aiEditMode, setAiEditMode] = useState<'replace' | 'insert_before' | 'insert_after'>('replace')
  const [aiEditPosition, setAiEditPosition] = useState<number>(0)
  const [selectedText, setSelectedText] = useState('')
  const [extracting, setExtracting] = useState<Record<number, boolean>>({})
  // 实体预览弹窗相关状态
  const [entityPreviewVisible, setEntityPreviewVisible] = useState(false)
  const [detectedEntities, setDetectedEntities] = useState<any>({
    characters: [],
    world_settings: []
  })
  const [editingCharacters, setEditingCharacters] = useState<any[]>([])
  const [editingSettings, setEditingSettings] = useState<any[]>([])
  const [entityExtractionChapterId, setEntityExtractionChapterId] = useState<number | null>(null)

  useEffect(() => {
    fetchProject()
    fetchChapters()
  }, [id])

  // 有趣的生成文案
  const generatingMessages = [
    "🤖 AI 正在努力创作中...",
    "✨ 正在构建故事情节...",
    "📝 正在塑造人物性格...",
    "🎨 正在打磨文字细节...",
    "💡 正在寻找灵感火花...",
    "🌟 正在编织精彩对话...",
    "🎭 正在设计人物互动...",
    "📚 正在查阅故事背景...",
    "🎬 正在构建场景画面...",
    "✍️ 正在润色文字表达...",
    "🌙 正在酝酿氛围情绪...",
    "🎪 正在编排情节起伏...",
    "🔮 正在预埋伏笔线索...",
    "🎵 正在调整叙事节奏...",
    "🎨 正在描绘环境细节...",
    "💫 马上就好，精彩即将呈现...",
    "🌸 正在注入情感元素...",
    "⚡ 正在推进情节发展...",
    "🎯 正在聚焦核心冲突...",
    "🌈 正在丰富故事层次..."
  ]

  // 启动生成动画
  const startGeneratingAnimation = () => {
    setGeneratingModalVisible(true)
    setGeneratingProgress(0)

    // 文案轮换（每 2 秒切换一次）
    let messageIndex = 0
    setGeneratingMessage(generatingMessages[0])

    generatingMessageInterval.current = setInterval(() => {
      messageIndex = (messageIndex + 1) % generatingMessages.length
      setGeneratingMessage(generatingMessages[messageIndex])
    }, 2000)

    // 进度条（模拟进度，60 秒内从 0% 到 95%）
    generatingProgressInterval.current = setInterval(() => {
      setGeneratingProgress(prev => {
        if (prev >= 95) return prev
        return prev + Math.random() * 3
      })
    }, 1000)
  }

  // 停止生成动画
  const stopGeneratingAnimation = () => {
    if (generatingMessageInterval.current) {
      clearInterval(generatingMessageInterval.current)
      generatingMessageInterval.current = null
    }
    if (generatingProgressInterval.current) {
      clearInterval(generatingProgressInterval.current)
      generatingProgressInterval.current = null
    }
    setGeneratingModalVisible(false)
    setGeneratingProgress(0)
  }

  // 组件卸载时清理定时器
  useEffect(() => {
    return () => {
      if (generatingMessageInterval.current) {
        clearInterval(generatingMessageInterval.current)
      }
      if (generatingProgressInterval.current) {
        clearInterval(generatingProgressInterval.current)
      }
    }
  }, [])

  const fetchProject = async () => {
    try {
      const response = await projectApi.get(Number(id))
      if (response.data.code !== 200) {
        console.error('加载项目失败:', response.data.message)
        return
      }
      setProject(response.data.data)
    } catch (error) {
      console.error('加载项目失败', error)
    }
  }

  const fetchChapters = async () => {
    setLoading(true)
    try {
      const response = await chapterApi.list(Number(id))
      if (response.data.code !== 200) {
        console.error('加载章节失败:', response.data.message)
        return
      }
      setChapters(response.data.data.chapters)

      // 自动计算下一章序号
      if (response.data.data.chapters.length > 0) {
        const maxChapter = Math.max(...response.data.data.chapters.map((c: Chapter) => c.chapter_number))
        setNewChapterNumber(maxChapter + 1)
      } else {
        setNewChapterNumber(1)
      }
    } catch (error) {
      console.error('加载章节失败', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchCharacters = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/characters/list/${id}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      const data = await response.json()
      if (data.code === 200) {
        setCharacters(data.data.characters || [])
      }
    } catch (error) {
      console.error('加载人物失败', error)
    }
  }

  const fetchWorldSettings = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/world-settings/list/${id}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      const data = await response.json()
      if (data.code === 200) {
        setWorldSettings(data.data.settings || [])
      }
    } catch (error) {
      console.error('加载世界观设定失败', error)
    }
  }

  // 打开高级生成配置时获取人物和世界观
  const handleOpenAdvancedGenerate = async () => {
    await Promise.all([
      fetchCharacters(),
      fetchWorldSettings()
    ])
    setAdvancedGenerateVisible(true)
  }

  // 处理高级生成
  const handleAdvancedGenerate = async (config: ChapterGenerateRequest) => {
    setAdvancedGenerating(true)
    setAdvancedGenerateVisible(false)

    // 启动全屏 loading 动画
    startGeneratingAnimation()

    try {
      const response = await fetch('http://localhost:8000/api/chapters/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(config)
      })

      const data = await response.json()

      if (data.code === 200) {
        stopGeneratingAnimation()

        // 显示版本选择界面
        setGeneratedVersions(data.data.versions)
        setCurrentChapterId(data.data.chapter_id) // 保存章节ID
        setContextUsed(data.data.context_used)
        setVersionPreviewVisible(true)

        message.success(`🎉 成功生成 ${data.data.versions.length} 个版本！请选择最满意的版本。`)
      } else {
        stopGeneratingAnimation()
        message.error(data.message || '生成失败')
      }
    } catch (error) {
      stopGeneratingAnimation()
      message.error('生成失败，请稍后重试')
      console.error('生成失败', error)
    } finally {
      setAdvancedGenerating(false)
    }
  }

  // 选择版本并保存
  const handleSelectVersion = async (versionId: string) => {
    try {
      const chapterId = currentChapterId
      if (!chapterId) {
        message.error('章节ID不存在，请重新生成')
        return
      }

      const response = await fetch(`http://localhost:8000/api/chapters/${chapterId}/select-version`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          version_id: versionId
        })
      })

      const data = await response.json()

      if (data.code === 200) {
        setVersionPreviewVisible(false)
        message.success('✅ 版本已保存！')

        // 更新当前章节的内容（如果正在编辑此章节）
        if (currentChapter && currentChapter.id === chapterId) {
          setCurrentChapter({
            ...currentChapter,
            content: data.data.content,
            word_count: data.data.word_count,
            version: data.data.version,
            status: data.data.status,
            updated_at: data.data.updated_at
          })
        } else {
          // 如果当前没有编辑章节，自动进入编辑模式
          const updatedChapter = data.data
          setCurrentChapter(updatedChapter)
        }

        // 刷新章节列表
        fetchChapters()
      } else {
        message.error(data.message || '保存失败')
      }
    } catch (error) {
      message.error('保存失败，请稍后重试')
      console.error('保存失败', error)
    }
  }

  // AI 文本编辑处理
  const handleAITextEdit = async (selectedTextContent: string, mode: 'replace' | 'insert_before' | 'insert_after', position?: number, customPrompt?: string) => {
    if (!currentChapter) {
      message.warning('请先选择章节')
      return
    }

    setAiEditing(true)
    setAiEditMode(mode)
    setSelectedText(selectedTextContent)
    setAiEditPosition(position || 0)

    // 启动全屏 loading
    startGeneratingAnimation()

    try {
      // 构建请求数据
      const requestData = {
        chapter_id: currentChapter.id,
        selected_text: selectedTextContent,
        mode: mode,
        position: position || 0,
        custom_prompt: customPrompt || undefined, // 添加自定义prompt
        context: {
          project_id: project?.id,
          chapter_number: currentChapter.chapter_number,
          prompt: customPrompt || undefined, // 将自定义prompt也放入context中
          // 这里可以添加前面章节的总结
        }
      }

      // 调用AI文本生成API
      const response = await fetch('http://localhost:8000/api/chapters/generate-text', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(requestData)
      })

      const data = await response.json()

      stopGeneratingAnimation()

      if (data.code === 200) {
        const generatedContent = data.data.content

        // 根据模式更新内容
        let newContent = currentChapter.content || ''

        if (mode === 'replace' && position !== undefined) {
          // 替换选中的文本
          const before = newContent.substring(0, position)
          const after = newContent.substring(position + selectedTextContent.length)
          newContent = before + generatedContent + after
        } else if (mode === 'insert_before') {
          // 在指定位置前插入
          const before = newContent.substring(0, position || 0)
          const after = newContent.substring(position || 0)
          newContent = before + generatedContent + after
        } else if (mode === 'insert_after') {
          // 在指定位置后插入
          const before = newContent.substring(0, position || 0)
          const after = newContent.substring(position || 0)
          newContent = before + after + generatedContent
        }

        // 更新章节内容
        setCurrentChapter({
          ...currentChapter,
          content: newContent,
          word_count: newContent.length
        })

        message.success('✨ AI 修改完成！')
      } else {
        message.error(data.message || 'AI 生成失败')
      }
    } catch (error) {
      stopGeneratingAnimation()
      message.error('AI 生成失败，请稍后重试')
      console.error('AI 生成失败', error)
    } finally {
      setAiEditing(false)
    }
  }

  const handleCreateChapter = async () => {
    if (!newChapterTitle.trim()) {
      message.error('请输入章节标题')
      return
    }

    setCreating(true)
    try {
      const response = await chapterApi.create({
        project_id: Number(id),
        title: newChapterTitle,
        chapter_number: newChapterNumber,
      })
      if (response.data.code !== 200) {
        message.error('创建章节失败: ' + response.data.message)
        return
      }
      message.success('章节创建成功')
      setCreateModalVisible(false)
      setNewChapterTitle('')
      fetchChapters()
    } catch (error) {
      message.error('创建章节失败')
      console.error('创建章节失败', error)
    } finally {
      setCreating(false)
    }
  }

  const handleEditOutline = () => {
    if (!currentChapter) return
    setOutlineContent(currentChapter.outline || '')
    setOutlineModalVisible(true)
  }

  const handleSaveOutline = async () => {
    if (!currentChapter) return

    setSaving(true)
    try {
      const response = await chapterApi.update(currentChapter.id, {
        outline: outlineContent
      })
      if (response.data.code === 200) {
        message.success('大纲保存成功')
        setCurrentChapter({
          ...currentChapter,
          outline: outlineContent
        })
        setOutlineModalVisible(false)
      } else {
        message.error('大纲保存失败: ' + response.data.message)
      }
    } catch (error) {
      message.error('大纲保存失败')
      console.error('大纲保存失败', error)
    } finally {
      setSaving(false)
    }
  }

  const handleSaveContent = async () => {
    if (!currentChapter) return

    setSaving(true)
    try {
      const response = await chapterApi.update(currentChapter.id, {
        content: currentChapter.content
      })
      if (response.data.code === 200) {
        message.success('内容保存成功')
        // 更新当前章节的word_count
        setCurrentChapter(response.data.data)
      } else {
        message.error('内容保存失败: ' + response.data.message)
      }
    } catch (error) {
      message.error('内容保存失败')
      console.error('内容保存失败', error)
    } finally {
      setSaving(false)
    }
  }

  const handleSelectChapter = async (chapter: Chapter) => {
    setLoadingChapter(true)
    try {
      const response = await chapterApi.get(chapter.id)
      if (response.data.code === 200) {
        setCurrentChapter(response.data.data)
      } else {
        message.error('加载章节失败: ' + response.data.message)
      }
    } catch (error) {
      message.error('加载章节失败')
      console.error('加载章节失败', error)
    } finally {
      setLoadingChapter(false)
    }
  }

  const handleStatusChange = async (newStatus: string) => {
    if (!currentChapter) return

    try {
      const response = await chapterApi.update(currentChapter.id, {
        status: newStatus as 'draft' | 'revising' | 'completed'
      })
      if (response.data.code === 200) {
        setCurrentChapter(response.data.data)
        message.success('状态已更新')
        // 刷新章节列表以更新状态显示
        fetchChapters()
      } else {
        message.error('状态更新失败: ' + response.data.message)
      }
    } catch (error) {
      message.error('状态更新失败')
      console.error('状态更新失败', error)
    }
  }

  const handleDeleteChapter = async (chapterId: number, chapterTitle: string, chapterNumber: number) => {
    try {
      const response = await chapterApi.delete(chapterId)
      if (response.data.code !== 200) {
        message.error('删除失败: ' + response.data.message)
        return
      }
      message.success(`第${chapterNumber}章《${chapterTitle}》已删除`)
      // 如果删除的是当前章节，返回列表
      if (currentChapter?.id === chapterId) {
        setCurrentChapter(null)
      }
      fetchChapters()
    } catch (error: any) {
      // 处理403无权限错误（401由全局拦截器处理）
      if (error.response?.status === 403) {
        message.error('您没有权限删除此章节')
        return
      }
      // 网络错误或其他错误
      if (!error.response) {
        message.error('网络连接失败，请检查网络')
        return
      }
      message.error('删除失败，请稍后重试')
      console.error('删除章节失败', error)
    }
  }

  const handleSaveStyleSettings = async (data: any) => {
    if (!project) return

    try {
      const response = await projectApi.update(Number(id), data)
      if (response.data.code === 200) {
        setProject(response.data.data)
      }
    } catch (error) {
      throw error
    }
  }

  const handleOpenContextAnalysis = () => {
    if (currentChapter) {
      setContextAnalysisVisible(true)
    } else {
      message.warning('请先选择一个章节')
    }
  }

  const handleCloseContextAnalysis = () => {
    setContextAnalysisVisible(false)
    setPlotDirection('')
  }

  const handleContextAnalysisConfirm = (selectedContext: any) => {
    // 处理用户选择的上下文
    console.log('Selected context:', selectedContext)

    // 保存用户的选择
    setSelectedContextFromAnalysis(selectedContext)

    // 关闭上下文分析，打开高级生成
    setContextAnalysisVisible(false)
    setPlotDirection('')

    // 自动打开高级生成
    setAdvancedGenerateVisible(true)

    message.success('✅ 已应用上下文设定，正在打开高级生成...')
  }

  const handleExtractEntities = async (chapterId: number) => {
    setExtracting({ ...extracting, [chapterId]: true })

    try {
      const result = await detectEntitiesFromChapter(chapterId)

      setDetectedEntities(result.data)
      setEntityExtractionChapterId(chapterId)

      // 默认选中所有非重复的实体，并设置为可编辑
      setEditingCharacters(
        result.data.characters.map((c: any) => ({
          ...c,
          checked: !c.is_duplicate,
          is_duplicate: c.is_duplicate
        }))
      )
      setEditingSettings(
        result.data.world_settings.map((s: any) => ({
          ...s,
          checked: !s.is_duplicate,
          is_duplicate: s.is_duplicate
        }))
      )

      // 显示预览弹窗
      setEntityPreviewVisible(true)

    } catch (error: any) {
      console.error('检测实体失败:', error)
      message.error(error.response?.data?.message || '检测实体失败，请稍后重试')
    } finally {
      setExtracting({ ...extracting, [chapterId]: false })
    }
  }

  const handleConfirmCreateEntities = async () => {
    if (!entityExtractionChapterId) return

    try {
      // 过滤出选中的实体，并移除不需要的字段
      const charactersToCreate = editingCharacters
        .filter(c => c.checked)
        .map(({ checked, is_duplicate, ...rest }) => rest)

      const settingsToCreate = editingSettings
        .filter(s => s.checked)
        .map(({ checked, is_duplicate, ...rest }) => rest)

      if (charactersToCreate.length === 0 && settingsToCreate.length === 0) {
        message.info('请选择要添加的实体')
        return
      }

      const result = await createEntities(entityExtractionChapterId, charactersToCreate, settingsToCreate)

      message.success(result.message || '实体添加成功')

      // 刷新人物和世界观列表
      await Promise.all([
        fetchCharacters(),
        fetchWorldSettings()
      ])

      // 关闭弹窗
      setEntityPreviewVisible(false)

    } catch (error: any) {
      console.error('创建实体失败:', error)
      message.error(error.response?.data?.message || '创建实体失败，请稍后重试')
    }
  }

  // 更新人物字段
  const updateCharacter = (index: number, field: string, value: any) => {
    const newCharacters = [...editingCharacters]
    newCharacters[index] = { ...newCharacters[index], [field]: value }
    setEditingCharacters(newCharacters)
  }

  // 更新世界观设定字段
  const updateSetting = (index: number, field: string, value: any) => {
    const newSettings = [...editingSettings]
    newSettings[index] = { ...newSettings[index], [field]: value }
    setEditingSettings(newSettings)
  }

  if (!project) {
    return (
      <div style={{ textAlign: 'center', padding: '100px' }}>
        <Spin size="large" />
      </div>
    )
  }

  return (
    <Layout style={{ height: 'calc(100vh - 64px)', background: '#fff' }}>
      {/* 中间：主活动区 - Tab切换 */}
      <Content style={{ overflowY: 'auto', background: '#fff' }}>
        {/* 页面头部 - 返回按钮和标题 */}
        <div style={{ padding: '16px 24px', borderBottom: '1px solid #f0f0f0', background: '#fafafa' }}>
          <Space>
            <Button
              icon={<ArrowLeftOutlined />}
              onClick={() => navigate('/dashboard')}
              style={{ marginRight: 8 }}
            >
              返回作品列表
            </Button>
            <span style={{ fontSize: '16px', fontWeight: 500, color: '#262626' }}>
              {project.title}
            </span>
          </Space>
        </div>
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          size="large"
          tabBarStyle={{ padding: '0 24px', margin: 0 }}
          items={[
            {
              key: 'chapters',
              label: (
                <span>
                  <BookOutlined /> 章节创作
                </span>
              ),
              children: (
                <div style={{ padding: '0 24px 24px' }}>
                  {loadingChapter ? (
                    <div style={{ textAlign: 'center', padding: '100px 0' }}>
                      <Spin size="large" tip="加载章节中..." />
                    </div>
                  ) : currentChapter ? (
                    <>
                      {/* 章节标题栏 */}
                      <Card
                        bordered={false}
                        style={{
                          borderRadius: 8,
                          marginBottom: 16,
                          backgroundColor: '#f5f5f5',
                        }}
                        bodyStyle={{ padding: '16px 24px' }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <div>
                            <h2 style={{ margin: 0, fontSize: '20px', fontWeight: 600, color: '#262626' }}>
                              第{currentChapter.chapter_number}章 {currentChapter.title}
                            </h2>
                            <Space style={{ marginTop: 8, color: '#8c8c8c', fontSize: '14px' }}>
                              <span>{currentChapter.word_count}字</span>
                              <span>·</span>
                              <span>状态：</span>
                              <Select
                                value={currentChapter.status}
                                onChange={handleStatusChange}
                                options={CHAPTER_STATUS_OPTIONS}
                                style={{
                                  fontSize: '14px',
                                  fontWeight: 500,
                                }}
                                size="small"
                              />
                              {currentChapter.outline && (
                                <>
                                  <span>·</span>
                                  <span>已有大纲</span>
                                </>
                              )}
                            </Space>
                          </div>
                          <Space>
                            <Button
                              icon={<ArrowLeftOutlined />}
                              onClick={() => setCurrentChapter(null)}
                              style={{ borderColor: '#d9d9d9' }}
                            >
                              返回列表
                            </Button>
                            <Button
                              icon={<EditOutlined />}
                              onClick={handleEditOutline}
                              style={{ borderColor: '#d9d9d9' }}
                            >
                              编辑大纲
                            </Button>
                            <Button
                              type="default"
                              icon={<ScanOutlined />}
                              onClick={() => handleExtractEntities(currentChapter.id)}
                              loading={extracting[currentChapter.id]}
                              disabled={!currentChapter.content}
                            >
                              提取实体
                            </Button>
                            <Dropdown
                              menu={{
                                items: [
                                  {
                                    key: 'context',
                                    label: '上下文分析',
                                    icon: <SearchOutlined />,
                                    onClick: handleOpenContextAnalysis
                                  },
                                  {
                                    key: 'advanced',
                                    label: '高级生成（多版本）',
                                    icon: <ThunderboltOutlined />,
                                    onClick: handleOpenAdvancedGenerate
                                  }
                                ]
                              }}
                              trigger={['click']}
                            >
                              <Button icon={<MoreOutlined />}>
                                AI工具 <DownOutlined />
                              </Button>
                            </Dropdown>
                            <Button
                              onClick={handleSaveContent}
                              loading={saving}
                              type="primary"
                            >
                              保存内容
                            </Button>
                          </Space>
                        </div>
                      </Card>

                      {/* 编辑区 - 使用智能文本编辑器 */}
                      <div style={{ marginTop: '24px' }}>
                        <SmartTextEditor
                          value={currentChapter.content || ''}
                          onChange={(content) => {
                            setCurrentChapter({
                              ...currentChapter,
                              content: content,
                              word_count: content.length,
                            })
                          }}
                          placeholder="在此处开始创作...&#10;&#10;提示：&#10;1. 可以直接在编辑框中撰写内容&#10;2. 选择文本后点击上方按钮可以AI修改选中的内容&#10;3. 内容会自动保存到本地状态，点击保存按钮提交到服务器"
                          autoSize={{
                            minRows: 20,
                            maxRows: 30,
                          }}
                          style={{
                            fontSize: '16px',
                            lineHeight: '1.8',
                            color: '#262626',
                            backgroundColor: '#fafafa',
                            borderColor: '#d9d9d9',
                            borderRadius: '4px',
                            padding: '16px',
                          }}
                          onAIGenerate={handleAITextEdit}
                          projectId={Number(id)}
                          chapterId={currentChapter.id}
                        />
                      </div>
                    </>
                  ) : (
                    <>
                      {/* 章节列表 */}
                      <Card
                        bordered={false}
                        style={{
                          borderRadius: 8,
                          marginBottom: 16,
                          backgroundColor: '#fafafa',
                        }}
                        bodyStyle={{ padding: '16px 24px' }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <h2 style={{ margin: 0, fontSize: '18px', fontWeight: 600, color: '#262626' }}>
                            章节列表
                          </h2>
                          <Button
                            type="primary"
                            icon={<PlusOutlined />}
                            onClick={() => setCreateModalVisible(true)}
                          >
                            新建章节
                          </Button>
                        </div>
                      </Card>

                      {loading ? (
                        <div style={{ textAlign: 'center', padding: '60px 0' }}>
                          <Spin size="large" tip="加载中..." />
                        </div>
                      ) : chapters.length === 0 ? (
                        <Empty
                          description={
                            <div>
                              <p style={{ fontSize: '16px', color: '#8c8c8c' }}>暂无章节</p>
                              <Button
                                type="primary"
                                icon={<PlusOutlined />}
                                size="large"
                                style={{ marginTop: 16 }}
                                onClick={() => setCreateModalVisible(true)}
                              >
                                创建第一章
                              </Button>
                            </div>
                          }
                          style={{ padding: '80px 0' }}
                        />
                      ) : (
                        <List
                          dataSource={chapters}
                          renderItem={(chapter) => (
                            <List.Item
                              style={{
                                cursor: loadingChapter ? 'wait' : 'pointer',
                                padding: '20px',
                                borderRadius: 8,
                                border: '1px solid #e8e8e8',
                                marginBottom: 12,
                                transition: 'all 0.3s',
                                backgroundColor: '#fff',
                              }}
                              onClick={(e) => {
                                // 避免点击删除按钮时触发选择章节
                                if (!(e.target as HTMLElement).closest('.delete-btn')) {
                                  handleSelectChapter(chapter)
                                }
                              }}
                              className="chapter-item"
                              onMouseEnter={(e) => {
                                if (!loadingChapter) {
                                  e.currentTarget.style.borderColor = '#1890ff'
                                  e.currentTarget.style.boxShadow = '0 2px 8px rgba(24,144,255,0.15)'
                                }
                              }}
                              onMouseLeave={(e) => {
                                e.currentTarget.style.borderColor = '#e8e8e8'
                                e.currentTarget.style.boxShadow = 'none'
                              }}
                              actions={[
                                <Popconfirm
                                  key="delete"
                                  title="删除章节"
                                  description={`确定要删除第${chapter.chapter_number}章《${chapter.title}》吗？此操作不可恢复。`}
                                  onConfirm={(e) => {
                                    e?.stopPropagation()
                                    handleDeleteChapter(chapter.id, chapter.title, chapter.chapter_number)
                                  }}
                                  onCancel={(e) => e?.stopPropagation()}
                                  okText="确定"
                                  cancelText="取消"
                                  okButtonProps={{ danger: true }}
                                >
                                  <Button
                                    type="text"
                                    danger
                                    icon={<DeleteOutlined />}
                                    size="small"
                                    className="delete-btn"
                                    onClick={(e) => e.stopPropagation()}
                                  >
                                    删除
                                  </Button>
                                </Popconfirm>
                              ]}
                            >
                              <List.Item.Meta
                                title={
                                  <div style={{ fontSize: '16px', fontWeight: 500, color: '#262626' }}>
                                    第{chapter.chapter_number}章 {chapter.title}
                                  </div>
                                }
                                description={
                                  <Space style={{ marginTop: '8px' }}>
                                    <span style={{
                                      fontSize: '14px',
                                      color: chapter.word_count > 0 ? '#52c41a' : '#8c8c8c'
                                    }}>
                                      {chapter.word_count}字
                                    </span>
                                    <span>·</span>
                                    <span style={{
                                      fontSize: '14px',
                                      color: PROJECT_STATUS_CONFIG[chapter.status as keyof typeof PROJECT_STATUS_CONFIG]?.color || '#8c8c8c',
                                      fontWeight: 500
                                    }}>
                                      {PROJECT_STATUS_CONFIG[chapter.status as keyof typeof PROJECT_STATUS_CONFIG]?.label || chapter.status}
                                    </span>
                                    {chapter.has_outline && (
                                      <>
                                        <span>·</span>
                                        <span style={{ fontSize: '14px', color: '#1890ff' }}>
                                          已有大纲
                                        </span>
                                      </>
                                    )}
                                  </Space>
                                }
                              />
                            </List.Item>
                          )}
                        />
                      )}
                    </>
                  )}
                </div>
              ),
            },
            {
              key: 'characters',
              label: (
                <span>
                  <TeamOutlined /> 人物管理
                </span>
              ),
              children: (
                <div style={{ padding: '0 24px 24px' }}>
                  <div style={{ padding: '16px 0', borderBottom: '1px solid #f0f0f0' }}>
                    <h2 style={{ margin: 0 }}>人物管理</h2>
                  </div>
                  <CharacterManagement projectId={Number(id)} />
                </div>
              ),
            },
            {
              key: 'world',
              label: (
                <span>
                  <GlobalOutlined /> 世界观设定
                </span>
              ),
              children: (
                <div style={{ padding: '0 24px 24px' }}>
                  <div style={{ padding: '16px 0', borderBottom: '1px solid #f0f0f0' }}>
                    <h2 style={{ margin: 0 }}>世界观设定</h2>
                  </div>
                  <WorldSettingManagement projectId={Number(id)} />
                </div>
              ),
            },
          ]}
        />
      </Content>

      {/* 右侧：智能上下文面板 (300px) */}
      <Sider width={300} theme="light" style={{ borderLeft: '1px solid #f0f0f0', overflowY: 'auto' }}>
        <div style={{ padding: '16px' }}>
          <h3 style={{ marginBottom: 16 }}>
            <BulbOutlined /> 上下文
          </h3>

          {/* 项目信息 */}
          <Card
            size="small"
            title={<span style={{ fontSize: '14px', fontWeight: 600 }}>📚 项目信息</span>}
            style={{ marginBottom: 16, borderRadius: 8 }}
            headStyle={{ backgroundColor: '#fafafa', borderBottom: '1px solid #f0f0f0' }}
          >
            <p style={{ margin: '8px 0', fontSize: '13px', color: '#595959' }}>
              <strong style={{ color: '#262626' }}>书名：</strong>{project.title}
            </p>
            <p style={{ margin: '8px 0', fontSize: '13px', color: '#595959' }}>
              <strong style={{ color: '#262626' }}>类型：</strong>
              {(() => {
                try {
                  const genres = JSON.parse(project.genre)
                  return Array.isArray(genres) ? genres.join('、') : project.genre
                } catch {
                  return project.genre || '-'
                }
              })()}
            </p>
            {project.summary && (
              <div style={{ margin: '8px 0' }}>
                <strong style={{ color: '#262626', fontSize: '13px' }}>简介：</strong>
                <div style={{
                  fontSize: '12px',
                  color: '#8c8c8c',
                  marginTop: '4px',
                  lineHeight: '1.6',
                  padding: '8px',
                  backgroundColor: '#fafafa',
                  borderRadius: '4px',
                  maxHeight: '120px',
                  overflowY: 'auto'
                }}>
                  {project.summary}
                </div>
              </div>
            )}
            <p style={{ margin: '8px 0', fontSize: '13px', color: '#595959' }}>
              <strong style={{ color: '#262626' }}>文风：</strong>
              <Button
                type="link"
                size="small"
                style={{ padding: 0, height: 'auto', fontSize: '13px' }}
                onClick={() => setStyleSettingsVisible(true)}
              >
                {project.style ? '设置文风' : '点击设置'}
              </Button>
            </p>
            <p style={{ margin: '8px 0', fontSize: '13px', color: '#595959' }}>
              <strong style={{ color: '#262626' }}>目标字数：</strong>{project.target_words_per_chapter}字/章
            </p>
          </Card>

          {/* 文风设置入口 */}
          <Card
            size="small"
            style={{ marginBottom: 16, borderRadius: 8, cursor: 'pointer', border: '1px dashed #d9d9d9' }}
            hoverable
            onClick={() => setStyleSettingsVisible(true)}
            bodyStyle={{ padding: '12px' }}
          >
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px', marginBottom: '8px' }}>🎨</div>
              <div style={{ fontSize: '14px', fontWeight: 500, color: '#262626' }}>
                文风设置
              </div>
              <div style={{ fontSize: '12px', color: '#8c8c8c', marginTop: '4px' }}>
                {project.style ? `当前：${project.style}` : '未设置'}
              </div>
            </div>
          </Card>

          {/* 快捷指令 - 已集成到智能编辑器中 */}
          {/* 原快捷指令功能已移至文本编辑器上方的工具栏 */}

          {/* 当前章节设定（有选中章节时显示） */}
          {currentChapter && activeTab === 'chapters' && (
            <Card
              size="small"
              title={<span style={{ fontSize: '14px', fontWeight: 600 }}>📖 当前章节</span>}
              style={{ marginBottom: 16, borderRadius: 8 }}
              headStyle={{ backgroundColor: '#fafafa', borderBottom: '1px solid #f0f0f0' }}
            >
              <p style={{ margin: '8px 0', fontSize: '13px', color: '#595959' }}>
                <strong style={{ color: '#262626' }}>章节号：</strong>第{currentChapter.chapter_number}章
              </p>
              <p style={{ margin: '8px 0', fontSize: '13px', color: '#595959' }}>
                <strong style={{ color: '#262626' }}>字数：</strong>{currentChapter.word_count}字
              </p>
              <p style={{ margin: '8px 0', fontSize: '13px', color: '#595959' }}>
                <strong style={{ color: '#262626' }}>状态：</strong>
                <span style={{
                  color: currentChapter.status === 'completed' ? '#52c41a' : '#faad14',
                  fontWeight: 500
                }}>
                  {currentChapter.status === 'completed' ? '已完成' : '草稿'}
                </span>
              </p>
              {currentChapter.display_summary && (
                <p style={{ margin: '8px 0', fontSize: '13px', color: '#595959' }}>
                  <strong style={{ color: '#262626' }}>摘要：</strong>
                  <div style={{ fontSize: '12px', color: '#8c8c8c', marginTop: 4, lineHeight: '1.6' }}>
                    {currentChapter.display_summary}
                  </div>
                </p>
              )}
            </Card>
          )}

          {/* 提示 */}
          <Card
            size="small"
            bordered={false}
            style={{
              background: 'linear-gradient(135deg, #f6ffed 0%, #f0f5ff 100%)',
              borderColor: '#b7eb8f',
              borderRadius: 8,
            }}
            bodyStyle={{ padding: '12px' }}
          >
            <p style={{ margin: 0, fontSize: '13px', color: '#52c41a', lineHeight: '1.6' }}>
              💡 <strong>提示：</strong>使用AI生成时，系统会自动注入当前项目的人物、世界观等设定，确保内容一致性。
            </p>
          </Card>
        </div>
      </Sider>

      {/* 创建章节模态框 */}
      <Modal
        title={<span style={{ fontSize: '18px', fontWeight: 600 }}>📝 新建章节</span>}
        open={createModalVisible}
        onOk={handleCreateChapter}
        onCancel={() => {
          setCreateModalVisible(false)
          setNewChapterTitle('')
        }}
        confirmLoading={creating}
        okText="创建"
        cancelText="取消"
        okButtonProps={{ style: { borderRadius: 6 } }}
        cancelButtonProps={{ style: { borderRadius: 6 } }}
      >
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <div>
            <div style={{ marginBottom: 8, fontWeight: 500, color: '#262626' }}>章节号：</div>
            <Input
              type="number"
              value={newChapterNumber}
              onChange={(e) => setNewChapterNumber(Number(e.target.value))}
              placeholder="请输入章节号"
              min={1}
              size="large"
            />
          </div>
          <div>
            <div style={{ marginBottom: 8, fontWeight: 500, color: '#262626' }}>章节标题：</div>
            <Input
              value={newChapterTitle}
              onChange={(e) => setNewChapterTitle(e.target.value)}
              placeholder="请输入章节标题"
              onPressEnter={handleCreateChapter}
              size="large"
            />
          </div>
        </Space>
      </Modal>

      {/* 编辑大纲模态框 */}
      <Modal
        title={<span style={{ fontSize: '18px', fontWeight: 600 }}>📋 编辑大纲</span>}
        open={outlineModalVisible}
        onOk={handleSaveOutline}
        onCancel={() => {
          setOutlineModalVisible(false)
          setOutlineContent('')
        }}
        confirmLoading={saving}
        okText="保存"
        cancelText="取消"
        width={600}
        okButtonProps={{ style: { borderRadius: 6 } }}
        cancelButtonProps={{ style: { borderRadius: 6 } }}
      >
        <div>
          <div style={{ marginBottom: 12, fontWeight: 500, color: '#262626' }}>大纲内容：</div>
          <Input.TextArea
            value={outlineContent}
            onChange={(e) => setOutlineContent(e.target.value)}
            placeholder="请输入本章大纲，包括主要情节、关键事件等...&#10;&#10;例如：&#10;1. 主角收到神秘信件&#10;2. 发现信中隐藏的线索&#10;3. 决定前往下一个地点调查"
            autoSize={{ minRows: 10, maxRows: 18 }}
            style={{ fontSize: '14px', lineHeight: '1.6' }}
          />
        </div>
      </Modal>

      {/* 文风设置模态框 */}
      <ProjectStyleSettings
        visible={styleSettingsVisible}
        onClose={() => setStyleSettingsVisible(false)}
        project={project}
        onSave={handleSaveStyleSettings}
      />

      {/* 上下文分析模态框 - 使用改进版 */}
      <ImprovedContextAnalysis
        visible={contextAnalysisVisible}
        projectId={Number(id)}
        chapterNumber={currentChapter?.chapter_number || 0}
        previousChapterId={chapters.find(c => c.chapter_number === (currentChapter?.chapter_number || 0) - 1)?.id}
        onConfirm={handleContextAnalysisConfirm}
        onCancel={handleCloseContextAnalysis}
      />

      {/* AI 生成全屏 Loading */}
      <Modal
        open={generatingModalVisible}
        closable={false}
        footer={null}
        centered
        width={500}
        styles={{
          body: {
            padding: '40px 24px',
            textAlign: 'center'
          }
        }}
      >
        <div style={{ marginBottom: '24px' }}>
          <Spin size="large" />
        </div>

        <div style={{ marginBottom: '20px' }}>
          <h3 style={{ fontSize: '16px', marginBottom: '8px', color: '#1890ff' }}>
            {generatingMessage}
          </h3>
          <p style={{ fontSize: '14px', color: '#666' }}>
            预计需要 20-60 秒，请稍候...
          </p>
        </div>

        <Progress
          percent={Math.min(generatingProgress, 95)}
          status="active"
          strokeColor={{
            '0%': '#108ee9',
            '100%': '#87d068',
          }}
          showInfo={false}
        />

        <p style={{ fontSize: '12px', color: '#999', marginTop: '16px' }}>
          💡 提示：生成时间取决于内容复杂度和网络状况
        </p>
      </Modal>

      {/* 高级生成配置 */}
      {project && (
        <AdvancedChapterGenerate
          visible={advancedGenerateVisible}
          onClose={() => {
            setAdvancedGenerateVisible(false)
            setSelectedContextFromAnalysis(null) // 关闭时清空上下文选择
          }}
          onGenerate={handleAdvancedGenerate}
          project={project}
          chapters={chapters}
          characters={characters}
          worldSettings={worldSettings}
          loading={advancedGenerating}
          initialContext={selectedContextFromAnalysis} // 传递上下文分析的选择
        />
      )}

      {/* 版本预览和选择 */}
      <VersionPreview
        visible={versionPreviewVisible}
        versions={generatedVersions}
        context={contextUsed}
        onSelect={handleSelectVersion}
        onClose={() => setVersionPreviewVisible(false)}
      />

      {/* 实体预览和确认弹窗 */}
      <Modal
        title="提取到的实体 - 可编辑"
        open={entityPreviewVisible}
        onOk={handleConfirmCreateEntities}
        onCancel={() => setEntityPreviewVisible(false)}
        width={900}
        okText="确认添加"
        cancelText="取消"
      >
        <Tabs
          defaultActiveKey="characters"
          items={[
            {
              key: 'characters',
              label: `人物 (${editingCharacters.filter(c => c.checked).length})`,
              children: (
                <div>
                  {editingCharacters.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '20px', color: '#999' }}>
                      未检测到人物
                    </div>
                  ) : (
                    <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
                      {editingCharacters.map((char: any, index: number) => (
                        <Card
                          key={index}
                          size="small"
                          style={{ marginBottom: '12px' }}
                          hoverable
                        >
                          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
                            <Checkbox
                              checked={char.checked}
                              disabled={char.is_duplicate}
                              onChange={(e) => {
                                const newCharacters = [...editingCharacters]
                                newCharacters[index].checked = e.target.checked
                                setEditingCharacters(newCharacters)
                              }}
                              style={{ marginTop: '4px' }}
                            />
                            <div style={{ flex: 1 }}>
                              <div style={{ marginBottom: '10px' }}>
                                <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>
                                  {char.is_duplicate && (
                                    <Tag color="orange" style={{ marginRight: '8px' }}>
                                      已存在
                                    </Tag>
                                  )}
                                </div>
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                                  <div>
                                    <label style={{ fontSize: '12px', color: '#666' }}>姓名 *</label>
                                    <Input
                                      value={char.name || ''}
                                      onChange={(e) => updateCharacter(index, 'name', e.target.value)}
                                      placeholder="姓名"
                                      size="small"
                                    />
                                  </div>
                                  <div>
                                    <label style={{ fontSize: '12px', color: '#666' }}>年龄</label>
                                    <Input
                                      value={char.age || ''}
                                      onChange={(e) => updateCharacter(index, 'age', e.target.value ? parseInt(e.target.value) : null)}
                                      placeholder="年龄"
                                      size="small"
                                      type="number"
                                    />
                                  </div>
                                  <div>
                                    <label style={{ fontSize: '12px', color: '#666' }}>性别</label>
                                    <Input
                                      value={char.gender || ''}
                                      onChange={(e) => updateCharacter(index, 'gender', e.target.value)}
                                      placeholder="性别"
                                      size="small"
                                    />
                                  </div>
                                  <div>
                                    <label style={{ fontSize: '12px', color: '#666' }}>身份</label>
                                    <Input
                                      value={char.identity || ''}
                                      onChange={(e) => updateCharacter(index, 'identity', e.target.value)}
                                      placeholder="身份/职业"
                                      size="small"
                                    />
                                  </div>
                                  <div>
                                    <label style={{ fontSize: '12px', color: '#666' }}>角色类型</label>
                                    <Select
                                      value={char.role || 'supporting'}
                                      onChange={(value) => updateCharacter(index, 'role', value)}
                                      size="small"
                                      style={{ width: '100%' }}
                                    >
                                      <Select.Option value="protagonist">主角</Select.Option>
                                      <Select.Option value="antagonist">反派</Select.Option>
                                      <Select.Option value="supporting">配角</Select.Option>
                                      <Select.Option value="minor">次要角色</Select.Option>
                                    </Select>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </Card>
                      ))}
                    </div>
                  )}
                </div>
              )
            },
            {
              key: 'world_settings',
              label: `世界观设定 (${editingSettings.filter(s => s.checked).length})`,
              children: (
                <div>
                  {editingSettings.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '20px', color: '#999' }}>
                      未检测到世界观设定
                    </div>
                  ) : (
                    <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
                      {editingSettings.map((setting: any, index: number) => (
                        <Card
                          key={index}
                          size="small"
                          style={{ marginBottom: '12px' }}
                          hoverable
                        >
                          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
                            <Checkbox
                              checked={setting.checked}
                              disabled={setting.is_duplicate}
                              onChange={(e) => {
                                const newSettings = [...editingSettings]
                                newSettings[index].checked = e.target.checked
                                setEditingSettings(newSettings)
                              }}
                              style={{ marginTop: '4px' }}
                            />
                            <div style={{ flex: 1 }}>
                              <div style={{ marginBottom: '10px' }}>
                                <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>
                                  {setting.is_duplicate && (
                                    <Tag color="orange" style={{ marginRight: '8px' }}>
                                      已存在
                                    </Tag>
                                  )}
                                  <Tag color="blue">
                                    {setting.setting_type}
                                  </Tag>
                                </div>
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                                  <div style={{ gridColumn: '1 / -1' }}>
                                    <label style={{ fontSize: '12px', color: '#666' }}>名称 *</label>
                                    <Input
                                      value={setting.name || ''}
                                      onChange={(e) => updateSetting(index, 'name', e.target.value)}
                                      placeholder="名称"
                                      size="small"
                                    />
                                  </div>
                                  <div style={{ gridColumn: '1 / -1' }}>
                                    <label style={{ fontSize: '12px', color: '#666' }}>类型</label>
                                    <Select
                                      value={setting.setting_type}
                                      onChange={(value) => updateSetting(index, 'setting_type', value)}
                                      size="small"
                                      style={{ width: '100%' }}
                                    >
                                      <Select.Option value="era">时代背景</Select.Option>
                                      <Select.Option value="region">地域/地点</Select.Option>
                                      <Select.Option value="rule">规则</Select.Option>
                                      <Select.Option value="culture">文化习俗</Select.Option>
                                      <Select.Option value="power">权力结构</Select.Option>
                                      <Select.Option value="location">具体地点</Select.Option>
                                      <Select.Option value="faction">势力/组织</Select.Option>
                                      <Select.Option value="item">重要物品</Select.Option>
                                      <Select.Option value="event">历史事件</Select.Option>
                                    </Select>
                                  </div>
                                  <div style={{ gridColumn: '1 / -1' }}>
                                    <label style={{ fontSize: '12px', color: '#666' }}>描述</label>
                                    <TextArea
                                      value={setting.description || ''}
                                      onChange={(e) => updateSetting(index, 'description', e.target.value)}
                                      placeholder="详细描述"
                                      size="small"
                                      rows={2}
                                    />
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </Card>
                      ))}
                    </div>
                  )}
                </div>
              )
            }
          ]}
        />
      </Modal>
    </Layout>
  )
}

export default ProjectDetail
