import { useEffect, useState } from 'react'
import { Table, Button, Modal, Form, Input, InputNumber, Select, message, Space, Popconfirm, Tabs, Tag } from 'antd'
import { PlusOutlined, DeleteOutlined, EditOutlined, UserOutlined } from '@ant-design/icons'
import { characterApi } from '../services/api'
import CharacterArcEditor from './CharacterArcEditor'
import VoiceStyleEditor from './VoiceStyleEditor'
import type { Character } from '../types'

const { TextArea } = Input
const { TabPane } = Tabs

interface CharacterManagementProps {
  projectId: number
}

const CharacterManagement = ({ projectId }: CharacterManagementProps) => {
  const [characters, setCharacters] = useState<Character[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingCharacter, setEditingCharacter] = useState<Character | null>(null)
  const [form] = Form.useForm()

  // 角色类型选项
  const roleOptions = [
    { value: 'protagonist', label: '主角', color: 'red' },
    { value: 'antagonist', label: '反派', color: 'orange' },
    { value: 'supporting', label: '配角', color: 'blue' },
    { value: 'minor', label: '次要角色', color: 'default' },
  ]

  const fetchCharacters = async () => {
    setLoading(true)
    try {
      const response = await characterApi.list(projectId)
      if (response.data.code !== 200) {
        message.error(response.data.message || '加载人物列表失败')
        return
      }
      setCharacters(response.data.data.characters)
      setTotal(response.data.data.total)
    } catch (error: any) {
      console.error('加载人物列表失败:', error)
      message.error('网络请求失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchCharacters()
  }, [projectId])

  const handleCreate = () => {
    setEditingCharacter(null)
    form.resetFields()
    setModalVisible(true)
  }

  const handleEdit = (character: Character) => {
    setEditingCharacter(character)
    form.setFieldsValue(character)
    setModalVisible(true)
  }

  const handleDelete = async (id: number, name: string) => {
    try {
      const response = await characterApi.delete(id)
      if (response.data.code !== 200) {
        message.error(response.data.message || '删除失败')
        return
      }
      message.success('删除成功')
      fetchCharacters()
    } catch (error: any) {
      console.error('删除人物失败:', error)
      message.error('网络请求失败')
    }
  }

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()

      if (!values.name || !values.name.trim()) {
        message.error('请输入人物姓名')
        return
      }

      const submitData = {
        ...values,
        project_id: projectId
      }

      if (editingCharacter) {
        // 更新
        const response = await characterApi.update(editingCharacter.id, submitData)
        if (response.data.code !== 200) {
          message.error(response.data.message || '更新失败')
          return
        }
        message.success('更新成功')
      } else {
        // 创建
        const response = await characterApi.create(submitData)
        if (response.data.code !== 200) {
          message.error(response.data.message || '创建失败')
          return
        }
        message.success('创建成功')
      }

      setModalVisible(false)
      form.resetFields()
      fetchCharacters()
    } catch (error: any) {
      console.error('操作失败:', error)
      message.error('操作失败')
    }
  }

  const columns = [
    {
      title: '姓名',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: Character) => (
        <Space>
          <UserOutlined />
          <a onClick={() => handleEdit(record)}>{text}</a>
        </Space>
      ),
    },
    {
      title: '角色',
      dataIndex: 'role',
      key: 'role',
      render: (role: string) => {
        const roleConfig = roleOptions.find(r => r.value === role)
        return <Tag color={roleConfig?.color}>{roleConfig?.label || role}</Tag>
      },
    },
    {
      title: '身份',
      dataIndex: 'identity',
      key: 'identity',
      render: (text: string) => text || '-',
    },
    {
      title: '年龄',
      dataIndex: 'age',
      key: 'age',
      render: (age: number) => age || '-',
    },
    {
      title: '性别',
      dataIndex: 'gender',
      key: 'gender',
      render: (gender: string) => gender || '-',
    },
    {
      title: '出场次数',
      dataIndex: 'appearance_count',
      key: 'appearance_count',
      render: (count: number) => `${count}次`,
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Character) => (
        <Space>
          <Button type="link" icon={<EditOutlined />} onClick={() => handleEdit(record)}>
            编辑
          </Button>
          <Popconfirm
            title="删除人物"
            description={`确定要删除人物"${record.name}"吗？此操作不可恢复。`}
            onConfirm={() => handleDelete(record.id, record.name)}
            okText="确定"
            cancelText="取消"
            okButtonProps={{ danger: true }}
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
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
        <h3>人物管理 ({total}人)</h3>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
          添加人物
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={characters}
        rowKey="id"
        loading={loading}
        pagination={false}
      />

      <Modal
        title={editingCharacter ? '编辑人物' : '添加人物'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => {
          setModalVisible(false)
          form.resetFields()
        }}
        width={800}
        style={{ top: 20 }}
      >
        <Form form={form} layout="vertical">
          <Tabs defaultActiveKey="basic">
            <TabPane tab="基础信息" key="basic">
              <Form.Item label="姓名" name="name" rules={[{ required: true, message: '请输入姓名' }]}>
                <Input placeholder="请输入人物姓名" />
              </Form.Item>

              <Form.Item label="角色类型" name="role" initialValue="supporting">
                <Select>
                  {roleOptions.map(option => (
                    <Select.Option key={option.value} value={option.value}>
                      {option.label}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>

              <Form.Item label="身份" name="identity">
                <Input placeholder="例如：剑圣、公主、平民等" />
              </Form.Item>

              <Form.Item label="年龄" name="age">
                <InputNumber min={0} max={10000} style={{ width: '100%' }} placeholder="请输入年龄" />
              </Form.Item>

              <Form.Item label="性别" name="gender">
                <Select placeholder="请选择性别" allowClear>
                  <Select.Option value="男">男</Select.Option>
                  <Select.Option value="女">女</Select.Option>
                  <Select.Option value="其他">其他</Select.Option>
                </Select>
              </Form.Item>

              <Form.Item label="籍贯" name="hometown">
                <Input placeholder="请输入籍贯" />
              </Form.Item>

              <Form.Item label="外貌描述" name="appearance">
                <TextArea rows={4} placeholder="描述人物的外貌特征" />
              </Form.Item>
            </TabPane>

            <TabPane tab="核心信息" key="core">
              <Form.Item label="性格标签" name="personality">
                <TextArea rows={3} placeholder="例如：MBTI类型、性格特点等（可用JSON格式存储多个标签）" />
              </Form.Item>

              <Form.Item label="核心动机" name="core_motivation">
                <TextArea rows={3} placeholder="驱动人物行动的核心原因" />
              </Form.Item>

              <Form.Item label="恐惧" name="fears">
                <TextArea rows={3} placeholder="人物最害怕的事物或情况" />
              </Form.Item>

              <Form.Item label="欲望" name="desires">
                <TextArea rows={3} placeholder="人物最渴望得到的东西" />
              </Form.Item>
            </TabPane>

            <TabPane tab="人物弧光" key="arc">
              <div style={{ marginBottom: 16, padding: '12px', backgroundColor: '#f0f5ff', borderRadius: '4px' }}>
                <p style={{ margin: 0, fontSize: '14px', color: '#1890ff' }}>
                  💡 人物弧光记录人物在故事中的多次转变过程，可以添加多条转变记录
                </p>
              </div>
              <Form.Item label="人物弧光记录" name="character_arcs">
                <CharacterArcEditor />
              </Form.Item>
            </TabPane>

            <TabPane tab="语音风格" key="voice">
              <div style={{ marginBottom: 16, padding: '12px', backgroundColor: '#f0f5ff', borderRadius: '4px' }}>
                <p style={{ margin: 0, fontSize: '14px', color: '#1890ff' }}>
                  💡 语言风格可以针对不同对象和场景设置不同的说话方式，帮助AI更准确地生成对话
                </p>
              </div>
              <Form.Item label="语言风格记录" name="voice_styles">
                <VoiceStyleEditor />
              </Form.Item>
            </TabPane>
          </Tabs>
        </Form>
      </Modal>
    </div>
  )
}

export default CharacterManagement
