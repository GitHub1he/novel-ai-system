import { useEffect, useState } from 'react'
import {
  Modal,
  Card,
  Row,
  Col,
  Checkbox,
  Button,
  Typography,
  Spin,
  message,
  Space,
  Divider,
  Tag,
  Tooltip,
  Collapse,
  List
} from 'antd'
import {
  UserOutlined,
  GlobalOutlined,
  ApartmentOutlined,
  BookOutlined,
  InfoCircleOutlined,
  CheckCircleOutlined,
  ExpandOutlined
} from '@ant-design/icons'
import axios from 'axios'

const { Title, Text, Paragraph } = Typography
const { Panel } = Collapse

interface ImprovedContextAnalysisProps {
  visible: boolean
  projectId: number
  chapterNumber: number
  previousChapterId?: number
  onConfirm: (selectedContext: {
    characters: number[]
    world_settings: number[]
    plot_nodes: number[]
    previousChapterSummary?: string
  }) => void
  onCancel: () => void
}

interface Character {
  id: number
  name: string
  role: string
  personality?: string
  appearance?: string
}

interface WorldSetting {
  id: number
  name: string
  setting_type: string
  description?: string
  is_core_rule: number
}

interface PlotNode {
  id: number
  title: string
  plot_type: string
  importance: string
  description?: string
}

interface ChapterSummary {
  chapter_number: number
  title: string
  summary: string
  key_events: string[]
  characters_mentioned: string[]
}

const ImprovedContextAnalysis: React.FC<ImprovedContextAnalysisProps> = ({
  visible,
  projectId,
  chapterNumber,
  previousChapterId,
  onConfirm,
  onCancel
}) => {
  const [loading, setLoading] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [characters, setCharacters] = useState<Character[]>([])
  const [worldSettings, setWorldSettings] = useState<WorldSetting[]>([])
  const [plotNodes, setPlotNodes] = useState<PlotNode[]>([])
  const [selectedCharacters, setSelectedCharacters] = useState<number[]>([])
  const [selectedWorldSettings, setSelectedWorldSettings] = useState<number[]>([])
  const [selectedPlotNodes, setSelectedPlotNodes] = useState<number[]>([])
  const [previousChapters, setPreviousChapters] = useState<ChapterSummary[]>([])
  const [autoSelected, setAutoSelected] = useState(true)

  // 加载项目数据
  useEffect(() => {
    if (visible) {
      loadProjectData()
    }
  }, [visible, projectId])

  const loadProjectData = async () => {
    setLoading(true)
    try {
      const token = localStorage.getItem('token')

      // 并行加载人物、世界观、情节节点
      const [charactersRes, worldSettingsRes, plotNodesRes] = await Promise.all([
        axios.get(`http://localhost:8000/api/characters/list/${projectId}`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`http://localhost:8000/api/world-settings/list/${projectId}`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`http://localhost:8000/api/plot-nodes/list/${projectId}`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ])

      if (charactersRes.data.code === 200) {
        setCharacters(charactersRes.data.data.characters || [])
      }

      if (worldSettingsRes.data.code === 200) {
        setWorldSettings(worldSettingsRes.data.data.settings || [])
      }

      if (plotNodesRes.data.code === 200) {
        setPlotNodes(plotNodesRes.data.data.plot_nodes || [])
      }

      // 自动选择核心规则和重要人物
      if (autoSelected) {
        autoSelectItems()
      }
    } catch (error) {
      console.error('加载数据失败:', error)
      message.error('加载数据失败')
    } finally {
      setLoading(false)
    }
  }

  // 自动选择重要的项目
  const autoSelectItems = () => {
    // 自动选择主角和配角
    const importantCharacters = characters
      .filter(c => c.role === 'protagonist' || c.role === 'supporting')
      .map(c => c.id)

    // 自动选择核心规则
    const coreRules = worldSettings
      .filter(s => s.is_core_rule === 1)
      .map(s => s.id)

    // 自动选择重要的情节节点
    const importantPlots = plotNodes
      .filter(p => p.importance === 'high')
      .map(p => p.id)

    setSelectedCharacters(importantCharacters)
    setSelectedWorldSettings(coreRules)
    setSelectedPlotNodes(importantPlots)
  }

  // 分析上下文（生成前面剧情总结）
  const handleAnalyzeContext = async () => {
    setAnalyzing(true)
    try {
      const token = localStorage.getItem('token')

      // 获取前面的章节
      const chaptersRes = await axios.get(`http://localhost:8000/api/chapters/list/${projectId}`, {
        headers: { Authorization: `Bearer ${token}` }
      })

      if (chaptersRes.data.code === 200) {
        const allChapters = chaptersRes.data.data.chapters || []
        // 获取当前章节之前的所有章节
        const prevChapters = allChapters
          .filter((c: any) => c.chapter_number < chapterNumber)
          .sort((a: any, b: any) => a.chapter_number - b.chapter_number)
          .slice(-3) // 只取最近3章

        setPreviousChapters(prevChapters)

        if (prevChapters.length === 0) {
          message.info('这是第一章，没有前面剧情')
        } else {
          const chaptersWithSummary = prevChapters.filter((c: any) => c.summary).length
          if (chaptersWithSummary < prevChapters.length) {
            message.warning(`已加载 ${prevChapters.length} 章，其中 ${chaptersWithSummary} 章有摘要，建议保存内容后自动生成摘要`)
          } else {
            message.success(`已加载 ${prevChapters.length} 章的剧情总结`)
          }
        }
      }
    } catch (error) {
      console.error('分析上下文失败:', error)
      message.error('分析上下文失败')
    } finally {
      setAnalyzing(false)
    }
  }

  // 组件打开时自动加载前面章节的摘要
  useEffect(() => {
    if (visible && chapterNumber > 1) {
      handleAnalyzeContext()
    }
  }, [visible, chapterNumber])

  const handleConfirm = () => {
    onConfirm({
      characters: selectedCharacters,
      world_settings: selectedWorldSettings,
      plot_nodes: selectedPlotNodes,
      previousChapterSummary: previousChapters.length > 0
        ? previousChapters.map(c => `第${c.chapter_number}章：${c.title}\n${c.summary}`).join('\n\n')
        : undefined
    })
    onCancel()
  }

  const getRoleLabel = (role: string) => {
    const roleMap: Record<string, string> = {
      'protagonist': '主角',
      'antagonist': '反派',
      'supporting': '配角',
      'minor': '次要角色'
    }
    return roleMap[role] || role
  }

  const getRoleColor = (role: string) => {
    const colorMap: Record<string, string> = {
      'protagonist': 'blue',
      'antagonist': 'red',
      'supporting': 'green',
      'minor': 'default'
    }
    return colorMap[role] || 'default'
  }

  return (
    <Modal
      title={
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <ExpandOutlined style={{ color: '#1890ff' }} />
          <span>上下文分析</span>
          <Tag color="blue">第{chapterNumber}章</Tag>
        </div>
      }
      open={visible}
      onCancel={onCancel}
      onOk={handleConfirm}
      width={900}
      okText="应用设定并开始生成"
      cancelText="取消"
      styles={{
        body: { padding: '24px', height: '60vh', overflow: 'auto' }
      }}
    >
      <Spin spinning={loading}>
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          {/* 提示卡片 */}
          <Card
            size="small"
            style={{
              background: 'linear-gradient(135deg, #e6f7ff 0%, #f0f5ff 100%)',
              borderColor: '#91d5ff',
            }}
          >
            <div style={{ fontSize: '13px', color: '#0050b3', lineHeight: '1.6' }}>
              💡 <strong>功能说明：</strong>选择本次生成要使用的人物、世界观和情节节点，点击"应用设定并开始生成"后会自动打开高级生成界面，这些设定会被预填充进去。
            </div>
          </Card>

          {/* 前面剧情总结 */}
          <Card
            size="small"
            title={
              <Space>
                <BookOutlined />
                <span>前面剧情总结</span>
              </Space>
            }
            extra={
              <Button
                size="small"
                icon={<ExpandOutlined />}
                loading={analyzing}
                onClick={handleAnalyzeContext}
              >
                分析剧情
              </Button>
            }
          >
            {previousChapters.length > 0 ? (
              <Collapse
                defaultActiveKey={[String(previousChapters.length - 1)]}
                size="small"
              >
                {previousChapters.map((chapter, index) => (
                  <Panel
                    header={`第${chapter.chapter_number}章：${chapter.title}`}
                    key={String(index)}
                  >
                    {chapter.summary ? (
                      <Paragraph
                        ellipsis={{ rows: 3, expandable: true, symbol: '展开' }}
                        style={{ fontSize: '13px', color: '#666' }}
                      >
                        {chapter.summary}
                      </Paragraph>
                    ) : (
                      <div style={{ padding: '12px', backgroundColor: '#fafafa', borderRadius: '4px', textAlign: 'center' }}>
                        <Text type="secondary" style={{ fontSize: '13px' }}>
                          📝 本章暂无摘要，保存内容后会自动生成
                        </Text>
                      </div>
                    )}
                    {chapter.key_events && chapter.key_events.length > 0 && (
                      <div style={{ marginTop: '8px' }}>
                        <Text strong style={{ fontSize: '12px' }}>关键事件：</Text>
                        <div style={{ marginTop: '4px' }}>
                          {chapter.key_events.map((event, i) => (
                            <Tag key={i} color="geekblue" style={{ marginBottom: '4px' }}>
                              {event}
                            </Tag>
                          ))}
                        </div>
                      </div>
                    )}
                  </Panel>
                ))}
              </Collapse>
            ) : (
              <div style={{ textAlign: 'center', padding: '20px 0', color: '#999' }}>
                <BookOutlined style={{ fontSize: '32px', marginBottom: '8px' }} />
                <div>这是第一章，没有前面剧情</div>
              </div>
            )}
          </Card>

          {/* 自动选择开关 */}
          <Card size="small">
            <Checkbox
              checked={autoSelected}
              onChange={(e) => {
                setAutoSelected(e.target.checked)
                if (e.target.checked) {
                  autoSelectItems()
                } else {
                  setSelectedCharacters([])
                  setSelectedWorldSettings([])
                  setSelectedPlotNodes([])
                }
              }}
            >
              <Space>
                <Text strong>自动选择重要设定</Text>
                <Tooltip title="自动选择主角、配角、核心规则和重要情节节点">
                  <InfoCircleOutlined style={{ color: '#999' }} />
                </Tooltip>
              </Space>
            </Checkbox>
          </Card>

          {/* 人物选择 */}
          <Card
            size="small"
            title={
              <Space>
                <UserOutlined />
                <span>登场人物</span>
                <Tag color={selectedCharacters.length > 0 ? 'success' : 'default'}>
                  已选 {selectedCharacters.length} 个
                </Tag>
              </Space>
            }
          >
            <Row gutter={[8, 8]}>
              {characters.map((character) => (
                <Col span={12} key={character.id}>
                  <Card
                    size="small"
                    hoverable
                    style={{
                      border: selectedCharacters.includes(character.id)
                        ? '2px solid #1890ff'
                        : '1px solid #d9d9d9'
                    }}
                    onClick={() => {
                      if (selectedCharacters.includes(character.id)) {
                        setSelectedCharacters(selectedCharacters.filter(id => id !== character.id))
                      } else {
                        setSelectedCharacters([...selectedCharacters, character.id])
                      }
                    }}
                  >
                    <Space direction="vertical" size="small" style={{ width: '100%' }}>
                      <div>
                        <Text strong>{character.name}</Text>
                        <Tag
                          color={getRoleColor(character.role)}
                          style={{ marginLeft: '8px', fontSize: '11px' }}
                        >
                          {getRoleLabel(character.role)}
                        </Tag>
                      </div>
                      {character.personality && (
                        <Text
                          ellipsis={{ tooltip: character.personality }}
                          style={{ fontSize: '12px', color: '#666' }}
                        >
                          {character.personality}
                        </Text>
                      )}
                    </Space>
                  </Card>
                </Col>
              ))}
            </Row>
          </Card>

          {/* 世界观设定选择 */}
          <Card
            size="small"
            title={
              <Space>
                <GlobalOutlined />
                <span>世界观设定</span>
                <Tag color={selectedWorldSettings.length > 0 ? 'success' : 'default'}>
                  已选 {selectedWorldSettings.length} 个
                </Tag>
              </Space>
            }
          >
            <Row gutter={[8, 8]}>
              {worldSettings.map((setting) => (
                <Col span={12} key={setting.id}>
                  <Card
                    size="small"
                    hoverable
                    style={{
                      border: selectedWorldSettings.includes(setting.id)
                        ? '2px solid #1890ff'
                        : '1px solid #d9d9d9'
                    }}
                    onClick={() => {
                      if (selectedWorldSettings.includes(setting.id)) {
                        setSelectedWorldSettings(selectedWorldSettings.filter(id => id !== setting.id))
                      } else {
                        setSelectedWorldSettings([...selectedWorldSettings, setting.id])
                      }
                    }}
                  >
                    <Space direction="vertical" size="small" style={{ width: '100%' }}>
                      <div>
                        <Text strong>{setting.name}</Text>
                        {setting.is_core_rule === 1 && (
                          <Tag color="gold" style={{ marginLeft: '8px', fontSize: '11px' }}>
                            核心
                          </Tag>
                        )}
                      </div>
                      <Text
                        ellipsis={{ tooltip: setting.description }}
                        style={{ fontSize: '12px', color: '#666' }}
                      >
                        {setting.description}
                      </Text>
                    </Space>
                  </Card>
                </Col>
              ))}
            </Row>
          </Card>

          {/* 情节节点选择 */}
          {plotNodes.length > 0 && (
            <Card
              size="small"
              title={
                <Space>
                  <ApartmentOutlined />
                  <span>情节节点</span>
                  <Tag color={selectedPlotNodes.length > 0 ? 'success' : 'default'}>
                    已选 {selectedPlotNodes.length} 个
                  </Tag>
                </Space>
              }
            >
              <Row gutter={[8, 8]}>
                {plotNodes.map((node) => (
                  <Col span={12} key={node.id}>
                    <Card
                      size="small"
                      hoverable
                      style={{
                        border: selectedPlotNodes.includes(node.id)
                          ? '2px solid #1890ff'
                          : '1px solid #d9d9d9'
                      }}
                      onClick={() => {
                        if (selectedPlotNodes.includes(node.id)) {
                          setSelectedPlotNodes(selectedPlotNodes.filter(id => id !== node.id))
                        } else {
                          setSelectedPlotNodes([...selectedPlotNodes, node.id])
                        }
                      }}
                    >
                      <Space direction="vertical" size="small" style={{ width: '100%' }}>
                        <Text strong>{node.title}</Text>
                        <Text
                          ellipsis={{ tooltip: node.description }}
                          style={{ fontSize: '12px', color: '#666' }}
                        >
                          {node.description}
                        </Text>
                      </Space>
                    </Card>
                  </Col>
                ))}
              </Row>
            </Card>
          )}
        </Space>
      </Spin>
    </Modal>
  )
}

export default ImprovedContextAnalysis
