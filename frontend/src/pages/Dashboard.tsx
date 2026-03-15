import { useEffect, useState } from 'react'
import { Card, Button, Table, Modal, Form, Input, InputNumber, message, Space } from 'antd'
import { PlusOutlined, BookOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { projectApi } from '../services/api'
import type { Project } from '../types'

const Dashboard = () => {
  const navigate = useNavigate()
  const [projects, setProjects] = useState<Project[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [form] = Form.useForm()

  const fetchProjects = async () => {
    setLoading(true)
    try {
      const response = await projectApi.list()
      setProjects(response.data.projects)
      setTotal(response.data.total)
    } catch (error) {
      message.error('加载项目列表失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchProjects()
  }, [])

  const handleCreate = async () => {
    try {
      const values = await form.validateFields()
      await projectApi.create(values)
      message.success('创建成功')
      setModalVisible(false)
      form.resetFields()
      fetchProjects()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '创建失败')
    }
  }

  const columns = [
    {
      title: '书名',
      dataIndex: 'title',
      key: 'title',
      render: (text: string, record: Project) => (
        <a onClick={() => navigate(`/project/${record.id}`)}>{text}</a>
      ),
    },
    {
      title: '作者',
      dataIndex: 'author',
      key: 'author',
    },
    {
      title: '类型',
      dataIndex: 'genre',
      key: 'genre',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const statusMap: Record<string, { text: string; color: string }> = {
          draft: { text: '草稿', color: 'default' },
          writing: { text: '写作中', color: 'processing' },
          completed: { text: '已完成', color: 'success' },
          archived: { text: '已归档', color: 'default' },
        }
        const statusInfo = statusMap[status] || { text: status, color: 'default' }
        return <span style={{ color: statusInfo.color }}>{statusInfo.text}</span>
      },
    },
    {
      title: '字数',
      dataIndex: 'total_words',
      key: 'total_words',
      render: (words: number) => `${words.toLocaleString()}字`,
    },
    {
      title: '章节',
      dataIndex: 'total_chapters',
      key: 'total_chapters',
      render: (count: number) => `${count}章`,
    },
  ]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h2>我的作品</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalVisible(true)}>
          创建新项目
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={projects}
        rowKey="id"
        loading={loading}
        pagination={{ total }}
      />

      <Modal
        title="创建新项目"
        open={modalVisible}
        onOk={handleCreate}
        onCancel={() => {
          setModalVisible(false)
          form.resetFields()
        }}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item label="书名" name="title" rules={[{ required: true, message: '请输入书名' }]}>
            <Input placeholder="请输入书名" />
          </Form.Item>
          <Form.Item label="作者" name="author" rules={[{ required: true, message: '请输入作者名' }]}>
            <Input placeholder="请输入作者名" />
          </Form.Item>
          <Form.Item label="类型" name="genre" rules={[{ required: true, message: '请选择类型' }]}>
            <Input placeholder="例如：玄幻、言情、都市等" />
          </Form.Item>
          <Form.Item label="简介" name="summary">
            <Input.TextArea rows={4} placeholder="请输入作品简介" />
          </Form.Item>
          <Form.Item label="每章目标字数" name="target_words_per_chapter" initialValue={2000}>
            <InputNumber min={500} max={10000} step={500} style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default Dashboard
