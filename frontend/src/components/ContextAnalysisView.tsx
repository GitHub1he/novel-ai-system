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
  Tooltip
} from 'antd'
import {
  UserOutlined,
  GlobalOutlined,
  BranchOutlined,
  PlusOutlined,
  MinusOutlined,
  InfoCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons'
import { contextAnalysisApi } from '../services/api'

const { Title, Text } = Typography
const { Option } = Select

interface ContextAnalysisViewProps {
  visible: boolean
  projectId: number
  plotDirection: string
  chapterNumber: number
  previousChapterId?: number
  onConfirm: (selectedContext: {
    characters: number[]
    world_settings: number[]
    plot_nodes: number[]
  }) => void
  onCancel: () => void
}

interface CharacterSuggestion {
  id: number
  name: string
  role: string
  personality?: string
  core_motivation?: string
}

interface WorldSettingSuggestion {
  id: number
  name: string
  type: string
  description?: string
  is_core_rule: boolean
}

interface PlotNodeSuggestion {
  id: number
  title: string
  type: string
  importance: string
  description?: string
  conflict_points?: string
}

interface AnalysisResult {
  validated_characters: CharacterSuggestion[]
  validated_world_settings: WorldSettingSuggestion[]
  validated_plot_nodes: PlotNodeSuggestion[]
}

const ContextAnalysisView: React.FC<ContextAnalysisViewProps> = ({
  visible,
  projectId,
  plotDirection,
  chapterNumber,
  previousChapterId,
  onConfirm,
  onCancel
}) => {
  const [loading, setLoading] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [selectedCharacters, setSelectedCharacters] = useState<number[]>([])
  const [selectedWorldSettings, setSelectedWorldSettings] = useState<number[]>([])
  const [selectedPlotNodes, setSelectedPlotNodes] = useState<number[]>([])

  // 获取角色类型的中文标签
  const getRoleLabel = (role: string) => {
    const roleMap: Record<string, string> = {
      'protagonist': '主角',
      'antagonist': '反派',
      'supporting': '配角',
      'minor': '次要角色'
    }
    return roleMap[role] || role
  }

  // 获取世界观类型的中文标签
  const getWorldSettingTypeLabel = (type: string) => {
    const typeMap: Record<string, string> = {
      'era': '时代',
      'region': '地区',
      'rule': '规则',
      'culture': '文化',
      'power': '力量体系',
      'location': '地点',
      'faction': '势力',
      'item': '物品',
      'event': '事件'
    }
    return typeMap[type] || type
  }

  // 获取情节类型的中文标签
  const getPlotTypeLabel = (type: string) => {
    const typeMap: Record<string, string> = {
      'meeting': '相遇',
      'betrayal': '背叛',
      'reconciliation': '和解',
      'conflict': '冲突',
      'revelation': '揭示',
      'transformation': '转变',
      'climax': '高潮',
      'resolution': '结局',
      'other': '其他'
    }
    return typeMap[type] || type
  }

  // 获取重要性中文标签
  const getImportanceLabel = (importance: string) => {
    const importanceMap: Record<string, string> = {
      'main': '主线',
      'branch': '支线',
      'background': '背景'
    }
    return importanceMap[importance] || importance
  }

  const fetchAnalysis = async () => {
    setLoading(true)
    try {
      const response = await contextAnalysisApi.analyze({
        project_id: projectId,
        plot_direction: plotDirection,
        previous_chapter_id: previousChapterId,
        chapter_number: chapterNumber
      })

      if (response.data.code !== 200) {
        message.error(response.data.message || '获取上下文分析失败')
        return
      }

      setAnalysisResult(response.data.data)

      // 默认选中所有建议项
      const defaultCharacters = response.data.data.validated_characters.map(c => c.id)
      const defaultWorldSettings = response.data.data.validated_world_settings.map(w => w.id)
      const defaultPlotNodes = response.data.data.validated_plot_nodes.map(p => p.id)

      setSelectedCharacters(defaultCharacters)
      setSelectedWorldSettings(defaultWorldSettings)
      setSelectedPlotNodes(defaultPlotNodes)
    } catch (error: any) {
      console.error('获取上下文分析失败:', error)
      message.error('网络请求失败')
    } finally {
      setLoading(false)
    }
  }

  const handleCharacterToggle = (characterId: number, checked: boolean) => {
    if (checked) {
      setSelectedCharacters([...selectedCharacters, characterId])
    } else {
      setSelectedCharacters(selectedCharacters.filter(id => id !== characterId))
    }
  }

  const handleWorldSettingToggle = (settingId: number, checked: boolean) => {
    if (checked) {
      setSelectedWorldSettings([...selectedWorldSettings, settingId])
    } else {
      setSelectedWorldSettings(selectedWorldSettings.filter(id => id !== settingId))
    }
  }

  const handlePlotNodeToggle = (nodeId: number, checked: boolean) => {
    if (checked) {
      setSelectedPlotNodes([...selectedPlotNodes, nodeId])
    } else {
      setSelectedPlotNodes(selectedPlotNodes.filter(id => id !== nodeId))
    }
  }

  const handleSelectAll = (type: 'characters' | 'world_settings' | 'plot_nodes', checked: boolean) => {
    if (analysisResult) {
      switch (type) {
        case 'characters':
          if (checked) {
            setSelectedCharacters(analysisResult.validated_characters.map(c => c.id))
          } else {
            setSelectedCharacters([])
          }
          break
        case 'world_settings':
          if (checked) {
            setSelectedWorldSettings(analysisResult.validated_world_settings.map(w => w.id))
          } else {
            setSelectedWorldSettings([])
          }
          break
        case 'plot_nodes':
          if (checked) {
            setSelectedPlotNodes(analysisResult.validated_plot_nodes.map(p => p.id))
          } else {
            setSelectedPlotNodes([])
          }
          break
      }
    }
  }

  const handleConfirm = () => {
    if (!analysisResult) return

    const selectedContext = {
      characters: selectedCharacters,
      world_settings: selectedWorldSettings,
      plot_nodes: selectedPlotNodes
    }

    onConfirm(selectedContext)
  }

  // 当modal打开时获取分析结果
  useEffect(() => {
    if (visible) {
      fetchAnalysis()
    }
  }, [visible])

  // 关闭时重置状态
  useEffect(() => {
    if (!visible) {
      setAnalysisResult(null)
      setSelectedCharacters([])
      setSelectedWorldSettings([])
      setSelectedPlotNodes([])
    }
  }, [visible])

  if (!visible) return null

  return (
    <Modal
      title={
        <Space>
          <InfoCircleOutlined />
          <span>AI上下文分析</span>
        </Space>
      }
      open={visible}
      onCancel={onCancel}
      footer={[
        <Button key="cancel" onClick={onCancel}>
          取消
        </Button>,
        <Button
          key="confirm"
          type="primary"
          onClick={handleConfirm}
          disabled={!analysisResult || loading}
        >
          确认并生成
        </Button>
      ]}
      width={1000}
      styles={{
        body: { maxHeight: '70vh', overflowY: 'auto' }
      }}
    >
      {loading ? (
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <Spin size="large" />
          <div style={{ marginTop: 20 }}>
            <Text>AI正在分析上下文，请稍候...</Text>
          </div>
        </div>
      ) : (
        <div>
          {analysisResult && (
            <>
              <Row gutter={[16, 16]}>
                {/* 角色建议 */}
                <Col span={8}>
                  <Card
                    size="small"
                    title={
                      <Space>
                        <UserOutlined />
                        <span>建议角色 ({selectedCharacters.length}/{analysisResult.validated_characters.length})</span>
                        <Checkbox
                          checked={selectedCharacters.length === analysisResult.validated_characters.length}
                          onChange={(e) => handleSelectAll('characters', e.target.checked)}
                          indeterminate={selectedCharacters.length > 0 && selectedCharacters.length < analysisResult.validated_characters.length}
                        />
                      </Space>
                    }
                    styles={{ body: { maxHeight: '400px', overflowY: 'auto' } }}
                  >
                    {analysisResult.validated_characters.map((character) => (
                      <div key={character.id} style={{ marginBottom: 12 }}>
                        <Checkbox
                          checked={selectedCharacters.includes(character.id)}
                          onChange={(e) => handleCharacterToggle(character.id, e.target.checked)}
                        >
                          <Space direction="vertical" size="small" style={{ width: '100%' }}>
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                              <Text strong>{character.name}</Text>
                              <Tag color={character.role === 'protagonist' ? 'red' :
                                       character.role === 'antagonist' ? 'orange' :
                                       character.role === 'supporting' ? 'blue' : 'default'}>
                                {getRoleLabel(character.role)}
                              </Tag>
                            </div>
                            {character.personality && (
                              <Text type="secondary" style={{ fontSize: 12 }}>
                                性格: {character.personality}
                              </Text>
                            )}
                            {character.core_motivation && (
                              <Text type="secondary" style={{ fontSize: 12 }}>
                                核心动机: {character.core_motivation}
                              </Text>
                            )}
                          </Space>
                        </Checkbox>
                      </div>
                    ))}
                    {analysisResult.validated_characters.length === 0 && (
                      <Text type="secondary">没有推荐的角色</Text>
                    )}
                  </Card>
                </Col>

                {/* 世界观设定建议 */}
                <Col span={8}>
                  <Card
                    size="small"
                    title={
                      <Space>
                        <GlobalOutlined />
                        <span>世界观设定 ({selectedWorldSettings.length}/{analysisResult.validated_world_settings.length})</span>
                        <Checkbox
                          checked={selectedWorldSettings.length === analysisResult.validated_world_settings.length}
                          onChange={(e) => handleSelectAll('world_settings', e.target.checked)}
                          indeterminate={selectedWorldSettings.length > 0 && selectedWorldSettings.length < analysisResult.validated_world_settings.length}
                        />
                      </Space>
                    }
                    styles={{ body: { maxHeight: '400px', overflowY: 'auto' } }}
                  >
                    {analysisResult.validated_world_settings.map((setting) => (
                      <div key={setting.id} style={{ marginBottom: 12 }}>
                        <Checkbox
                          checked={selectedWorldSettings.includes(setting.id)}
                          onChange={(e) => handleWorldSettingToggle(setting.id, e.target.checked)}
                        >
                          <Space direction="vertical" size="small" style={{ width: '100%' }}>
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                              <Text strong>{setting.name}</Text>
                              <Tag color={setting.is_core_rule ? 'red' : 'default'}>
                                {getWorldSettingTypeLabel(setting.type)}
                              </Tag>
                            </div>
                            {setting.description && (
                              <Text type="secondary" style={{ fontSize: 12 }}>
                                {setting.description}
                              </Text>
                            )}
                          </Space>
                        </Checkbox>
                      </div>
                    ))}
                    {analysisResult.validated_world_settings.length === 0 && (
                      <Text type="secondary">没有推荐的世界观设定</Text>
                    )}
                  </Card>
                </Col>

                {/* 情节节点建议 */}
                <Col span={8}>
                  <Card
                    size="small"
                    title={
                      <Space>
                        <BranchOutlined />
                        <span>情节节点 ({selectedPlotNodes.length}/{analysisResult.validated_plot_nodes.length})</span>
                        <Checkbox
                          checked={selectedPlotNodes.length === analysisResult.validated_plot_nodes.length}
                          onChange={(e) => handleSelectAll('plot_nodes', e.target.checked)}
                          indeterminate={selectedPlotNodes.length > 0 && selectedPlotNodes.length < analysisResult.validated_plot_nodes.length}
                        />
                      </Space>
                    }
                    styles={{ body: { maxHeight: '400px', overflowY: 'auto' } }}
                  >
                    {analysisResult.validated_plot_nodes.map((node) => (
                      <div key={node.id} style={{ marginBottom: 12 }}>
                        <Checkbox
                          checked={selectedPlotNodes.includes(node.id)}
                          onChange={(e) => handlePlotNodeToggle(node.id, e.target.checked)}
                        >
                          <Space direction="vertical" size="small" style={{ width: '100%' }}>
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                              <Text strong>{node.title}</Text>
                              <Space>
                                <Tag color={node.importance === 'main' ? 'red' :
                                         node.importance === 'branch' ? 'blue' : 'default'}>
                                  {getImportanceLabel(node.importance)}
                                </Tag>
                                <Tag>{getPlotTypeLabel(node.type)}</Tag>
                              </Space>
                            </div>
                            {node.description && (
                              <Text type="secondary" style={{ fontSize: 12 }}>
                                {node.description}
                              </Text>
                            )}
                            {node.conflict_points && (
                              <Tooltip title={`冲突点: ${node.conflict_points}`}>
                                <Text type="secondary" style={{ fontSize: 12 }}>
                                  <ExclamationCircleOutlined style={{ marginRight: 4 }} />
                                  包含冲突元素
                                </Text>
                              </Tooltip>
                            )}
                          </Space>
                        </Checkbox>
                      </div>
                    ))}
                    {analysisResult.validated_plot_nodes.length === 0 && (
                      <Text type="secondary">没有推荐的情节节点</Text>
                    )}
                  </Card>
                </Col>
              </Row>

              {/* 摘要信息 */}
              <div style={{ marginTop: 16, padding: 16, backgroundColor: '#f5f5f5', borderRadius: 8 }}>
                <Title level={5}>摘要</Title>
                <Row gutter={16}>
                  <Col span={8}>
                    <Text>已选择角色: <Text strong>{selectedCharacters.length}</Text> 个</Text>
                  </Col>
                  <Col span={8}>
                    <Text>已选择世界观设定: <Text strong>{selectedWorldSettings.length}</Text> 个</Text>
                  </Col>
                  <Col span={8}>
                    <Text>已选择情节节点: <Text strong>{selectedPlotNodes.length}</Text> 个</Text>
                  </Col>
                </Row>
                <div style={{ marginTop: 8 }}>
                  {selectedCharacters.length + selectedWorldSettings.length + selectedPlotNodes.length === 0 ? (
                    <Text type="secondary">
                      请至少选择一个上下文元素以进行内容生成
                    </Text>
                  ) : (
                    <Text type="secondary">
                      <CheckCircleOutlined style={{ color: 'green', marginRight: 4 }} />
                      已选择足够的上下文元素，AI将根据这些信息生成相关内容
                    </Text>
                  )}
                </div>
              </div>

              {plotDirection && (
                <div style={{ marginTop: 16, padding: 12, backgroundColor: '#e6f7ff', borderRadius: 8 }}>
                  <Text type="secondary">
                    <strong>当前情节方向:</strong> {plotDirection}
                  </Text>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </Modal>
  )
}

export default ContextAnalysisView