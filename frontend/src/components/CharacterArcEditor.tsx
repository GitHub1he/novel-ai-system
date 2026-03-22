import { useState, useEffect, useRef } from 'react'
import { Button, Card, Input, Space, Row, Col, Typography, Popconfirm, Modal, message, Tag } from 'antd'
import { PlusOutlined, DeleteOutlined, EditOutlined, ImportOutlined } from '@ant-design/icons'

const { Text } = Typography
const { TextArea } = Input

export interface CharacterArc {
  period: string
  event: string
  before: string
  after: string
}

interface CharacterArcEditorProps {
  value?: CharacterArc[]
  onChange?: (value: CharacterArc[]) => void
}

const CharacterArcEditor = ({ value = [], onChange }: CharacterArcEditorProps) => {
  const [arcs, setArcs] = useState<CharacterArc[]>(value || [])
  const [editingIndex, setEditingIndex] = useState<number | null>(null)
  const [importModalVisible, setImportModalVisible] = useState(false)
  const [importJsonText, setImportJsonText] = useState('')

  const isUserEditingRef = useRef(false)
  const isInitializedRef = useRef(false)

  useEffect(() => {
    if (!isInitializedRef.current) {
      isInitializedRef.current = true
      return
    }

    if (!isUserEditingRef.current) {
      setArcs((value || []).filter((item): item is CharacterArc => item != null))
    }
  }, [value])

  const handleAdd = () => {
    isUserEditingRef.current = true
    const newArcs = [...arcs, { period: '', event: '', before: '', after: '' }]
    setArcs(newArcs)
    setEditingIndex(newArcs.length - 1)
  }

  const handleDelete = (index: number) => {
    isUserEditingRef.current = true
    const newArcs = arcs.filter((_, i) => i !== index)
    setArcs(newArcs)
    updateParent(newArcs)
    requestAnimationFrame(() => {
      isUserEditingRef.current = false
    })
  }

  const handleEdit = (index: number) => {
    isUserEditingRef.current = true
    setEditingIndex(index)
  }

  const handleSave = (index: number, field: string, value: string) => {
    const newArcs = [...arcs]
    newArcs[index] = { ...newArcs[index], [field]: value }
    setArcs(newArcs)
    updateParent(newArcs)
  }

  const handleFinishEdit = () => {
    setEditingIndex(null)
    requestAnimationFrame(() => {
      isUserEditingRef.current = false
    })
  }

  const handleCancel = () => {
    setEditingIndex(null)
    isUserEditingRef.current = false
  }

  const updateParent = (newArcs: CharacterArc[]) => {
    onChange?.(newArcs.filter(arc => arc.period || arc.event || arc.before || arc.after))
  }

  const handleImportClick = () => {
    setImportJsonText(JSON.stringify(arcs, null, 2))
    setImportModalVisible(true)
  }

  const handleImportConfirm = () => {
    try {
      const parsed = JSON.parse(importJsonText)
      if (!Array.isArray(parsed)) {
        message.error('JSON必须是数组格式')
        return
      }

      setArcs(parsed)
      updateParent(parsed)
      setImportModalVisible(false)
      isUserEditingRef.current = false
      message.success(`成功导入 ${parsed.length} 条人物弧光`)
    } catch (e) {
      message.error('JSON格式错误，请检查')
    }
  }

  return (
    <div>
      <Space direction="vertical" style={{ width: '100%' }} size="small">
        {arcs.map((arc, index) => {
          const isEditing = editingIndex === index

          return (
            <Card
              key={index}
              size="small"
              style={{ backgroundColor: isEditing ? '#f0f5ff' : '#fafafa' }}
              extra={
                <Space size="small">
                  {!isEditing && (
                    <>
                      <Button
                        type="link"
                        size="small"
                        icon={<EditOutlined />}
                        onClick={() => handleEdit(index)}
                      >
                        编辑
                      </Button>
                      <Popconfirm
                        title="确认删除"
                        description="确定要删除这条人物弧光吗？"
                        onConfirm={() => handleDelete(index)}
                        okText="确定"
                        cancelText="取消"
                      >
                        <Button
                          type="link"
                          size="small"
                          danger
                          icon={<DeleteOutlined />}
                        />
                      </Popconfirm>
                    </>
                  )}
                  {isEditing && (
                    <Button type="link" size="small" onClick={handleFinishEdit}>
                      完成
                    </Button>
                  )}
                </Space>
              }
            >
              {isEditing ? (
                <Space direction="vertical" style={{ width: '100%' }} size="small">
                  <div>
                    <Text strong>时期/章节：</Text>
                    <Input
                      placeholder="例如：第1-10章、前期、中期等"
                      value={arc.period}
                      onChange={(e) => handleSave(index, 'period', e.target.value)}
                      style={{ marginTop: 4 }}
                    />
                  </div>
                  <div>
                    <Text strong>转折事件：</Text>
                    <TextArea
                      rows={2}
                      placeholder="人物发生改变的关键事件"
                      value={arc.event}
                      onChange={(e) => handleSave(index, 'event', e.target.value)}
                      style={{ marginTop: 4 }}
                    />
                  </div>
                  <div>
                    <Text strong>转变前状态：</Text>
                    <TextArea
                      rows={2}
                      placeholder="人物在事件前的状态"
                      value={arc.before}
                      onChange={(e) => handleSave(index, 'before', e.target.value)}
                      style={{ marginTop: 4 }}
                    />
                  </div>
                  <div>
                    <Text strong>转变后状态：</Text>
                    <TextArea
                      rows={2}
                      placeholder="人物在事件后的状态"
                      value={arc.after}
                      onChange={(e) => handleSave(index, 'after', e.target.value)}
                      style={{ marginTop: 4 }}
                    />
                  </div>
                </Space>
              ) : (
                <Space direction="vertical" style={{ width: '100%' }} size="small">
                  <Row gutter={8}>
                    <Col span={6}>
                      <Text type="secondary">时期/章节</Text>
                      <div style={{ marginTop: 4 }}>
                        {arc.period || <Text type="secondary">未设置</Text>}
                      </div>
                    </Col>
                    <Col span={18}>
                      <Text type="secondary">转折事件</Text>
                      <div style={{ marginTop: 4 }}>
                        {arc.event || <Text type="secondary">未设置</Text>}
                      </div>
                    </Col>
                  </Row>
                  <Row gutter={8}>
                    <Col span={11}>
                      <Tag color="orange">转变前</Tag>
                      <div style={{ marginTop: 4, fontSize: '12px' }}>
                        {arc.before || <Text type="secondary">未设置</Text>}
                      </div>
                    </Col>
                    <Col span={2} style={{ textAlign: 'center' }}>
                      <Text type="secondary">→</Text>
                    </Col>
                    <Col span={11}>
                      <Tag color="green">转变后</Tag>
                      <div style={{ marginTop: 4, fontSize: '12px' }}>
                        {arc.after || <Text type="secondary">未设置</Text>}
                      </div>
                    </Col>
                  </Row>
                </Space>
              )}
            </Card>
          )
        })}

        <Space style={{ marginTop: 8, width: '100%' }}>
          <Button
            type="dashed"
            icon={<PlusOutlined />}
            onClick={handleAdd}
            style={{ flex: 1 }}
          >
            添加人物弧光
          </Button>
          <Button
            type="dashed"
            icon={<ImportOutlined />}
            onClick={handleImportClick}
            style={{ flex: 1 }}
          >
            导入JSON
          </Button>
        </Space>

        {arcs.length === 0 && (
          <div style={{ textAlign: 'center', padding: '20px', color: '#999' }}>
            暂无人物弧光记录，点击上方按钮添加
          </div>
        )}
      </Space>

      <Modal
        title="导入人物弧光JSON"
        open={importModalVisible}
        onOk={handleImportConfirm}
        onCancel={() => setImportModalVisible(false)}
        width={700}
        okText="导入"
        cancelText="取消"
      >
        <div style={{ marginBottom: 12 }}>
          <Text type="secondary">
            粘贴JSON格式的人物弧光数组，导入后将覆盖现有记录
          </Text>
        </div>
        <Input.TextArea
          rows={12}
          value={importJsonText}
          onChange={(e) => setImportJsonText(e.target.value)}
          placeholder={`[
  {
    "period": "第1-10章",
    "event": "初次修炼",
    "before": "懵懂少年",
    "after": "坚定信念"
  },
  {
    "period": "第50章",
    "event": "师父牺牲",
    "before": "依赖师父",
    "after": "独立成长"
  }
]`}
          style={{ fontFamily: 'monospace' }}
        />
      </Modal>
    </div>
  )
}

export default CharacterArcEditor
