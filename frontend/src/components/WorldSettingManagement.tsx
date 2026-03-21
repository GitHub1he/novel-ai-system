import { useEffect, useState } from 'react'
import { Table, Button, Modal, Form, Input, Select, Switch, message, Space, Popconfirm, Tabs, Tag } from 'antd'
import { PlusOutlined, DeleteOutlined, EditOutlined, GlobalOutlined } from '@ant-design/icons'
import { worldSettingApi } from '../services/api'
import EntitySelector from './EntitySelector'
import AttributesEditor from './AttributesEditor'
import type { WorldSetting } from '../types'

const { TextArea } = Input
const { TabPane } = Tabs

interface WorldSettingManagementProps {
  projectId: number
}

const WorldSettingManagement = ({ projectId }: WorldSettingManagementProps) => {
  const [settings, setSettings] = useState<WorldSetting[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingSetting, setEditingSetting] = useState<WorldSetting | null>(null)
  const [form] = Form.useForm()

  // 设定类型选项
  const settingTypeOptions = [
    { value: 'era', label: '时代', color: 'blue' },
    { value: 'region', label: '地域', color: 'green' },
    { value: 'rule', label: '规则', color: 'red' },
    { value: 'culture', label: '文化', color: 'purple' },
    { value: 'power', label: '权力', color: 'orange' },
    { value: 'location', label: '地点', color: 'cyan' },
    { value: 'faction', label: '势力', color: 'magenta' },
    { value: 'item', label: '物品', color: 'lime' },
    { value: 'event', label: '事件', color: 'gold' },
  ]

  const fetchSettings = async () => {
    setLoading(true)
    try {
      const response = await worldSettingApi.list(projectId)
      if (response.data.code !== 200) {
        message.error(response.data.message || '加载世界观设定失败')
        return
      }
      setSettings(response.data.data.settings)
      setTotal(response.data.data.total)
    } catch (error: any) {
      console.error('加载世界观设定失败:', error)
      message.error('网络请求失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchSettings()
  }, [projectId])

  const handleCreate = () => {
    setEditingSetting(null)
    form.resetFields()
    setModalVisible(true)
  }

  const handleEdit = (setting: WorldSetting) => {
    setEditingSetting(setting)

    // 转换 related_entities 从 JSON 字符串/对象到数组
    const formValues = {
      ...setting,
      related_entities: Array.isArray(setting.related_entities)
        ? setting.related_entities
        : []
      // attributes 直接传入对象，由 AttributesEditor 组件处理
    }

    form.setFieldsValue(formValues)
    setModalVisible(true)
  }

  const handleDelete = async (id: number, name: string, isCoreRule: number) => {
    if (isCoreRule === 1) {
      message.error('核心规则不可删除')
      return
    }

    try {
      const response = await worldSettingApi.delete(id)
      if (response.data.code !== 200) {
        message.error(response.data.message || '删除失败')
        return
      }
      message.success('删除成功')
      fetchSettings()
    } catch (error: any) {
      console.error('删除世界观设定失败:', error)
      message.error('网络请求失败')
    }
  }

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()

      if (!values.name || !values.name.trim()) {
        message.error('请输入设定名称')
        return
      }

      // 处理 is_core_rule 字段：将布尔值转换为整数
      const processedCoreRule = typeof values.is_core_rule === 'boolean'
        ? (values.is_core_rule ? 1 : 0)
        : values.is_core_rule

      // 准备提交数据（attributes 字段由 AttributesEditor 直接返回对象）
      const submitData = {
        ...values,
        is_core_rule: processedCoreRule,
        project_id: projectId
      }

      if (editingSetting) {
        // 更新
        const response = await worldSettingApi.update(editingSetting.id, submitData)
        if (response.data.code !== 200) {
          message.error(response.data.message || '更新失败')
          return
        }
        message.success('更新成功')
      } else {
        // 创建
        const response = await worldSettingApi.create(submitData)
        if (response.data.code !== 200) {
          message.error(response.data.message || '创建失败')
          return
        }
        message.success('创建成功')
      }

      setModalVisible(false)
      form.resetFields()
      fetchSettings()
    } catch (error: any) {
      console.error('操作失败:', error)
      message.error('操作失败')
    }
  }

  // 按类型分组显示
  const groupedSettings = settings.reduce((acc, setting) => {
    if (!acc[setting.setting_type]) {
      acc[setting.setting_type] = []
    }
    acc[setting.setting_type].push(setting)
    return acc
  }, {} as Record<string, WorldSetting[]>)

  const columns = [
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: WorldSetting) => (
        <Space>
          <GlobalOutlined />
          <a onClick={() => handleEdit(record)}>{text}</a>
          {record.is_core_rule === 1 && <Tag color="red" style={{ marginLeft: 8 }}>核心</Tag>}
        </Space>
      ),
    },
    {
      title: '类型',
      dataIndex: 'setting_type',
      key: 'setting_type',
      render: (type: string) => {
        const typeConfig = settingTypeOptions.find(t => t.value === type)
        return <Tag color={typeConfig?.color}>{typeConfig?.label || type}</Tag>
      },
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      render: (text: string) => text || '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_: any, record: WorldSetting) => (
        <Space>
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => handleEdit(record)}>
            编辑
          </Button>
          <Popconfirm
            title="删除设定"
            description={`确定要删除"${record.name}"吗？${record.is_core_rule === 1 ? '(核心规则不可删除)' : ''}`}
            onConfirm={() => handleDelete(record.id, record.name, record.is_core_rule)}
            okText="确定"
            cancelText="取消"
            okButtonProps={{ danger: true }}
            disabled={record.is_core_rule === 1}
          >
            <Button type="link" size="small" danger icon={<DeleteOutlined />} disabled={record.is_core_rule === 1}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h3>世界观设定 ({total}项)</h3>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
          添加设定
        </Button>
      </div>

      {/* 按类型分组显示 */}
      <Tabs defaultActiveKey="all">
        <TabPane tab={`全部 (${total})`} key="all">
          <Table
            columns={columns}
            dataSource={settings}
            rowKey="id"
            loading={loading}
            pagination={false}
            size="small"
          />
        </TabPane>

        {settingTypeOptions.map(type => (
          <TabPane
            tab={`${type.label} (${groupedSettings[type.value]?.length || 0})`}
            key={type.value}
          >
            <Table
              columns={columns}
              dataSource={groupedSettings[type.value] || []}
              rowKey="id"
              loading={loading}
              pagination={false}
              size="small"
            />
          </TabPane>
        ))}
      </Tabs>

      <Modal
        title={editingSetting ? '编辑世界观设定' : '添加世界观设定'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => {
          setModalVisible(false)
          form.resetFields()
        }}
        width={700}
        style={{ top: 20 }}
      >
        <Form form={form} layout="vertical">
          <Form.Item label="设定名称" name="name" rules={[{ required: true, message: '请输入设定名称' }]}>
            <Input placeholder="例如：中唐时期、长安城、修真体系等" />
          </Form.Item>

          <Form.Item label="设定类型" name="setting_type" initialValue="region" rules={[{ required: true, message: '请选择设定类型' }]}>
            <Select>
              {settingTypeOptions.map(option => (
                <Select.Option key={option.value} value={option.value}>
                  {option.label}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            label="核心规则"
            name="is_core_rule"
            valuePropName="checked"
            tooltip="核心规则不可删除，是故事的基础逻辑（如：无魔法、人均寿命80岁）"
          >
            <Switch checkedChildren="是" unCheckedChildren="否" />
          </Form.Item>

          <Form.Item label="详细描述" name="description">
            <TextArea rows={6} placeholder="详细描述这个设定的内容、特点、影响等" />
          </Form.Item>

          <Form.Item label="扩展属性" name="attributes">
            <AttributesEditor />
          </Form.Item>

          <Form.Item label="关联实体" name="related_entities">
            <EntitySelector
              projectId={projectId}
              placeholder="选择关联的人物或世界观设定"
            />
          </Form.Item>

          <Form.Item label="图片URL" name="image">
            <Input placeholder="地图、图标等图片URL" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default WorldSettingManagement
