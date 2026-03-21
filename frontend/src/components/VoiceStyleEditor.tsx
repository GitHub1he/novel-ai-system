import { useState, useEffect, useRef } from 'react'
import { Button, Card, Input, Space, Row, Col, Typography, Popconfirm, Modal, message, Tag, Select } from 'antd'
import { PlusOutlined, DeleteOutlined, EditOutlined, ImportOutlined } from '@ant-design/icons'

const { Text } = Typography
const { TextArea } = Input

export interface VoiceStyle {
  target: string
  scenario: string
  style: string
  sample: string
}

interface VoiceStyleEditorProps {
  value?: VoiceStyle[]
  onChange?: (value: VoiceStyle[]) => void
}

// 常见对象选项
const TARGET_OPTIONS = [
  '主角',
  '反派',
  '朋友',
  '长辈',
  '下属',
  '陌生人',
  '爱人',
  '仇敌',
  '师徒',
  '同门',
  '家人',
  '通用',
]

// 常见场景选项
const SCENARIO_OPTIONS = [
  '日常对话',
  '战斗',
  '谈判',
  '训话',
  '求情',
  '愤怒',
  '悲伤',
  '开心',
  '威胁',
  '嘲讽',
  '安慰',
  '解释',
]

const VoiceStyleEditor = ({ value = [], onChange }: VoiceStyleEditorProps) => {
  const [styles, setStyles] = useState<VoiceStyle[]>(value)
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
      setStyles(value || [])
    }
  }, [value])

  const handleAdd = () => {
    isUserEditingRef.current = true
    const newStyles = [...styles, { target: '', scenario: '', style: '', sample: '' }]
    setStyles(newStyles)
    setEditingIndex(newStyles.length - 1)
  }

  const handleDelete = (index: number) => {
    isUserEditingRef.current = true
    const newStyles = styles.filter((_, i) => i !== index)
    setStyles(newStyles)
    updateParent(newStyles)
    requestAnimationFrame(() => {
      isUserEditingRef.current = false
    })
  }

  const handleEdit = (index: number) => {
    isUserEditingRef.current = true
    setEditingIndex(index)
  }

  const handleSave = (index: number, field: string, value: string) => {
    const newStyles = [...styles]
    newStyles[index] = { ...newStyles[index], [field]: value }
    setStyles(newStyles)
    updateParent(newStyles)
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

  const updateParent = (newStyles: VoiceStyle[]) => {
    onChange?.(newStyles.filter(s => s.target || s.scenario || s.style || s.sample))
  }

  const handleImportClick = () => {
    setImportJsonText(JSON.stringify(styles, null, 2))
    setImportModalVisible(true)
  }

  const handleImportConfirm = () => {
    try {
      const parsed = JSON.parse(importJsonText)
      if (!Array.isArray(parsed)) {
        message.error('JSON必须是数组格式')
        return
      }

      setStyles(parsed)
      updateParent(parsed)
      setImportModalVisible(false)
      isUserEditingRef.current = false
      message.success(`成功导入 ${parsed.length} 条语言风格`)
    } catch (e) {
      message.error('JSON格式错误，请检查')
    }
  }

  return (
    <div>
      <Space direction="vertical" style={{ width: '100%' }} size="small">
        {styles.map((styleItem, index) => {
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
                        description="确定要删除这条语言风格吗？"
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
                  <Row gutter={8}>
                    <Col span={12}>
                      <Text strong>对象：</Text>
                      <Select
                        mode="tags"
                        placeholder="选择或输入对象"
                        value={styleItem.target ? [styleItem.target] : []}
                        onChange={(values) => handleSave(index, 'target', values[0] || '')}
                        options={TARGET_OPTIONS.map(t => ({ label: t, value: t }))}
                        style={{ width: '100%', marginTop: 4 }}
                      />
                    </Col>
                    <Col span={12}>
                      <Text strong>场景：</Text>
                      <Select
                        mode="tags"
                        placeholder="选择或输入场景"
                        value={styleItem.scenario ? [styleItem.scenario] : []}
                        onChange={(values) => handleSave(index, 'scenario', values[0] || '')}
                        options={SCENARIO_OPTIONS.map(s => ({ label: s, value: s }))}
                        style={{ width: '100%', marginTop: 4 }}
                      />
                    </Col>
                  </Row>
                  <div>
                    <Text strong>风格描述：</Text>
                    <TextArea
                      rows={2}
                      placeholder="描述说话特点，例如：简短有力、文绉绉、满口方言等"
                      value={styleItem.style}
                      onChange={(e) => handleSave(index, 'style', e.target.value)}
                      style={{ marginTop: 4 }}
                    />
                  </div>
                  <div>
                    <Text strong>样本对话：</Text>
                    <TextArea
                      rows={3}
                      placeholder="输入一段对话，供AI学习模仿"
                      value={styleItem.sample}
                      onChange={(e) => handleSave(index, 'sample', e.target.value)}
                      style={{ marginTop: 4 }}
                    />
                  </div>
                </Space>
              ) : (
                <Space direction="vertical" style={{ width: '100%' }} size="small">
                  <Row gutter={8}>
                    <Col span={12}>
                      <Tag color="blue">对象</Tag>
                      <div style={{ marginTop: 4 }}>
                        {styleItem.target || <Text type="secondary">未设置</Text>}
                      </div>
                    </Col>
                    <Col span={12}>
                      <Tag color="purple">场景</Tag>
                      <div style={{ marginTop: 4 }}>
                        {styleItem.scenario || <Text type="secondary">未设置</Text>}
                      </div>
                    </Col>
                  </Row>
                  <div>
                    <Text type="secondary">风格描述：</Text>
                    <div style={{ marginTop: 4, fontSize: '12px' }}>
                      {styleItem.style || <Text type="secondary">未设置</Text>}
                    </div>
                  </div>
                  <div>
                    <Text type="secondary">样本对话：</Text>
                    <div style={{
                      marginTop: 4,
                      padding: '8px',
                      backgroundColor: '#f5f5f5',
                      borderRadius: '4px',
                      fontSize: '12px',
                      fontStyle: 'italic'
                    }}>
                      {styleItem.sample || <Text type="secondary">未设置</Text>}
                    </div>
                  </div>
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
            添加语言风格
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

        {styles.length === 0 && (
          <div style={{ textAlign: 'center', padding: '20px', color: '#999' }}>
            暂无语言风格记录，点击上方按钮添加
          </div>
        )}
      </Space>

      <Modal
        title="导入语言风格JSON"
        open={importModalVisible}
        onOk={handleImportConfirm}
        onCancel={() => setImportModalVisible(false)}
        width={700}
        okText="导入"
        cancelText="取消"
      >
        <div style={{ marginBottom: 12 }}>
          <Text type="secondary">
            粘贴JSON格式的语言风格数组，导入后将覆盖现有记录
          </Text>
        </div>
        <Input.TextArea
          rows={12}
          value={importJsonText}
          onChange={(e) => setImportJsonText(e.target.value)}
          placeholder={`[
  {
    "target": "主角",
    "scenario": "日常对话",
    "style": "温柔体贴，常用关心语气",
    "sample": "你今天还好吗？有没有受伤？"
  },
  {
    "target": "敌人",
    "scenario": "战斗",
    "style": "冷酷无情，言简意赅",
    "sample": "今日，你必死！"
  }
]`}
          style={{ fontFamily: 'monospace' }}
        />
      </Modal>
    </div>
  )
}

export default VoiceStyleEditor
