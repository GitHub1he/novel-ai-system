import { useState, useEffect, useRef } from 'react'
import { Button, Card, Input, Space, Row, Col, Typography, Popconfirm, Modal, message } from 'antd'
import { PlusOutlined, DeleteOutlined, EditOutlined, ImportOutlined } from '@ant-design/icons'

const { Text } = Typography

interface AttributeItem {
  key: string
  value: string
}

interface AttributesEditorProps {
  value?: Record<string, any>
  onChange?: (value: Record<string, any>) => void
}

const AttributesEditor = ({ value = {}, onChange }: AttributesEditorProps) => {
  const [items, setItems] = useState<AttributeItem[]>(
    Object.entries(value).map(([key, val]) => ({
      key,
      value: typeof val === 'object' ? JSON.stringify(val) : String(val)
    }))
  )
  const [editingIndex, setEditingIndex] = useState<number | null>(null)
  const [importModalVisible, setImportModalVisible] = useState(false)
  const [importJsonText, setImportJsonText] = useState('')

  // 使用 ref 来同步控制是否应该从 value 更新 items
  const isUserEditingRef = useRef(false)
  const isInitializedRef = useRef(false)

  // 只在组件首次挂载或外部 value 变化时同步
  useEffect(() => {
    if (!isInitializedRef.current) {
      // 首次初始化
      isInitializedRef.current = true
      return
    }

    // 只有在非用户编辑状态下才从 value 同步
    if (!isUserEditingRef.current) {
      const newItems = Object.entries(value).map(([key, val]) => ({
        key,
        value: typeof val === 'object' ? JSON.stringify(val) : String(val)
      }))
      setItems(newItems)
    }
  }, [value])

  const handleAdd = () => {
    isUserEditingRef.current = true
    const newItems = [...items, { key: '', value: '' }]
    setItems(newItems)
    setEditingIndex(newItems.length - 1)
    // 添加时不更新父组件，等到保存时再更新
  }

  const handleDelete = (index: number) => {
    isUserEditingRef.current = true
    const newItems = items.filter((_, i) => i !== index)
    setItems(newItems)
    updateParent(newItems)
    // 使用 requestAnimationFrame 确保在下一个渲染周期重置标志
    requestAnimationFrame(() => {
      isUserEditingRef.current = false
    })
  }

  const handleEdit = (index: number) => {
    isUserEditingRef.current = true
    setEditingIndex(index)
  }

  const handleSave = (index: number, key: string, val: string) => {
    const newItems = [...items]
    newItems[index] = { key: key.trim(), value: val.trim() }
    setItems(newItems)
    setEditingIndex(null)

    // 先更新父组件
    updateParent(newItems)

    // 使用 requestAnimationFrame 确保在下一个渲染周期重置标志
    requestAnimationFrame(() => {
      isUserEditingRef.current = false
    })
  }

  const handleCancel = () => {
    setEditingIndex(null)
    isUserEditingRef.current = false
  }

  const updateParent = (newItems: AttributeItem[]) => {
    const obj = newItems.reduce((acc, item) => {
      if (item.key) {
        // 尝试解析值是否为 JSON
        try {
          acc[item.key] = JSON.parse(item.value)
        } catch {
          acc[item.key] = item.value
        }
      }
      return acc
    }, {} as Record<string, any>)

    onChange?.(obj)
  }

  const handleImportClick = () => {
    setImportJsonText(JSON.stringify(
      items.reduce((acc, item) => {
        if (item.key) {
          try {
            acc[item.key] = JSON.parse(item.value)
          } catch {
            acc[item.key] = item.value
          }
        }
        return acc
      }, {} as Record<string, any>),
      null,
      2
    ))
    setImportModalVisible(true)
  }

  const handleImportConfirm = () => {
    try {
      const parsed = JSON.parse(importJsonText)
      if (typeof parsed !== 'object' || parsed === null) {
        message.error('JSON必须是对象格式')
        return
      }

      const newItems = Object.entries(parsed).map(([key, val]) => ({
        key,
        value: typeof val === 'object' ? JSON.stringify(val) : String(val)
      }))

      setItems(newItems)
      updateParent(newItems)
      setImportModalVisible(false)
      isUserEditingRef.current = false
      message.success(`成功导入 ${newItems.length} 个属性`)
    } catch (e) {
      message.error('JSON格式错误，请检查')
    }
  }

  return (
    <div>
      <Space direction="vertical" style={{ width: '100%' }} size="small">
        {items.map((item, index) => {
          const isEditing = editingIndex === index

          return (
            <Card
              key={index}
              size="small"
              style={{ backgroundColor: isEditing ? '#f0f5ff' : '#fafafa' }}
            >
              {isEditing ? (
                <Row gutter={8} align="middle">
                  <Col span={10}>
                    <Input
                      placeholder="属性名"
                      defaultValue={item.key}
                      onPressEnter={(e) => {
                        const target = e.target as HTMLInputElement
                        handleSave(index, target.value, item.value)
                      }}
                      autoFocus
                    />
                  </Col>
                  <Col span={12}>
                    <Input
                      placeholder="属性值"
                      defaultValue={item.value}
                      onPressEnter={(e) => {
                        const input = e.currentTarget.parentElement?.parentElement
                          ?.previousElementSibling?.querySelector('input') as HTMLInputElement
                        if (input) {
                          handleSave(index, input.value, e.currentTarget.value)
                        }
                      }}
                    />
                  </Col>
                  <Col span={2}>
                    <Space size="small">
                      <Button
                        type="link"
                        size="small"
                        onClick={() => {
                          const inputs = document.querySelectorAll(
                            `.ant-card[data-editing="${index}"] input`
                          )
                          const keyInput = inputs[0] as HTMLInputElement
                          const valueInput = inputs[1] as HTMLInputElement
                          handleSave(index, keyInput.value, valueInput.value)
                        }}
                      >
                        保存
                      </Button>
                      <Button type="link" size="small" onClick={handleCancel}>
                        取消
                      </Button>
                    </Space>
                  </Col>
                </Row>
              ) : (
                <Row gutter={8} align="middle">
                  <Col span={10}>
                    <Text strong>{item.key || '<空属性名>'}</Text>
                  </Col>
                  <Col span={12}>
                    <Text ellipsis={{ tooltip: item.value }}>
                      {item.value || '<空值>'}
                    </Text>
                  </Col>
                  <Col span={2}>
                    <Space size="small">
                      <Button
                        type="link"
                        size="small"
                        icon={<EditOutlined />}
                        onClick={() => handleEdit(index)}
                      />
                      <Popconfirm
                        title="确认删除"
                        description="确定要删除这个属性吗？"
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
                    </Space>
                  </Col>
                </Row>
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
            添加属性
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

        {items.length === 0 && (
          <div style={{ textAlign: 'center', padding: '20px', color: '#999' }}>
            暂无扩展属性，点击上方按钮添加
          </div>
        )}
      </Space>

      <Modal
        title="导入JSON"
        open={importModalVisible}
        onOk={handleImportConfirm}
        onCancel={() => setImportModalVisible(false)}
        width={600}
        okText="导入"
        cancelText="取消"
      >
        <div style={{ marginBottom: 12 }}>
          <Text type="secondary">
            粘贴JSON格式的属性对象，导入后将覆盖现有属性
          </Text>
        </div>
        <Input.TextArea
          rows={12}
          value={importJsonText}
          onChange={(e) => setImportJsonText(e.target.value)}
          placeholder='{
  "属性名1": "属性值1",
  "属性名2": "属性值2",
  "属性名3": {"嵌套": "对象"}
}'
          style={{ fontFamily: 'monospace' }}
        />
      </Modal>
    </div>
  )
}

export default AttributesEditor
