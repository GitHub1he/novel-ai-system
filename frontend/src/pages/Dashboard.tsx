import { useEffect, useState } from 'react'
import { Card, Button, Table, Modal, Form, Input, InputNumber, Select, message, Space, Popconfirm } from 'antd'
import { PlusOutlined, BookOutlined, DeleteOutlined } from '@ant-design/icons'
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

  // 常见小说类型选项
  const genreOptions = [
    // 幻想类
    { value: '玄幻', label: '玄幻' },
    { value: '武侠', label: '武侠' },
    { value: '仙侠', label: '仙侠' },
    { value: '修真', label: '修真' },
    { value: '科幻', label: '科幻' },
    // 现实类
    { value: '都市', label: '都市' },
    { value: '青春', label: '青春' },
    { value: '历史', label: '历史' },
    { value: '军事', label: '军事' },
    // 情感类
    { value: '言情', label: '言情' },
    { value: '纯爱', label: '纯爱' },
    { value: '耽美', label: '耽美' },
    // 流行元素
    { value: '重生', label: '重生' },
    { value: '穿越', label: '穿越' },
    { value: '系统', label: '系统' },
    { value: '无敌', label: '无敌' },
    { value: '热血', label: '热血' },
    // 其他
    { value: '游戏', label: '游戏' },
    { value: '悬疑', label: '悬疑' },
    { value: '灵异', label: '灵异' },
    { value: '同人', label: '同人' },
    { value: '轻小说', label: '轻小说' },
    { value: '其他', label: '其他' },
  ]

  const fetchProjects = async () => {
    setLoading(true)
    try {
      const response = await projectApi.list()
      // 检查业务状态码
      if (response.data.code !== 200) {
        message.error(response.data.message || '加载项目列表失败')
        return
      }
      // 成功，设置数据
      setProjects(response.data.data.projects)
      setTotal(response.data.data.total)
    } catch (error: any) {
      // 网络错误
      console.error('加载项目列表失败:', error)
      message.error('网络请求失败，请检查网络连接')
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

      // 确保必填字段不为空
      if (!values.title || !values.title.trim()) {
        message.error('请输入书名')
        return
      }
      if (!values.author || !values.author.trim()) {
        message.error('请输入作者名')
        return
      }
      if (!values.genre || !values.genre || values.genre.length === 0) {
        message.error('请选择至少一个类型')
        return
      }

      // 将 genre 数组转换为 JSON 字符串
      const submitData = {
        ...values,
        genre: Array.isArray(values.genre) ? JSON.stringify(values.genre) : values.genre
      }

      const response = await projectApi.create(submitData)

      // 检查业务状态码
      if (response.data.code !== 200) {
        message.error(response.data.message || '创建失败')
        return
      }

      // 成功
      message.success('创建成功')
      setModalVisible(false)
      form.resetFields()
      fetchProjects()
    } catch (error: any) {
      // 网络错误或表单验证失败
      console.error('创建项目失败:', error)
      message.error('网络请求失败，请检查网络连接')
    }
  }

  const handleDelete = async (id: number, title: string) => {
    try {
      const response = await projectApi.delete(id)

      // 检查业务状态码
      if (response.data.code !== 200) {
        message.error(response.data.message || '删除失败')
        return
      }

      // 成功
      message.success('删除成功')
      fetchProjects()
    } catch (error: any) {
      // 网络错误
      console.error('删除项目失败:', error)
      message.error('网络请求失败，请检查网络连接')
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
      render: (genre: string) => {
        if (!genre) return '-'
        try {
          const genres = JSON.parse(genre)
          return Array.isArray(genres) ? genres.join('、') : genre
        } catch {
          return genre
        }
      },
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
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Project) => (
        <Space>
          <Popconfirm
            title="删除项目"
            description={`确定要删除《${record.title}》吗？此操作不可恢复。`}
            onConfirm={() => handleDelete(record.id, record.title)}
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
          <Form.Item
            label="类型"
            name="genre"
            rules={[{ required: true, message: '请选择至少一个类型' }]}
            tooltip="支持多选，例如：玄幻 + 修仙 + 热血"
          >
            <Select
              mode="tags"
              placeholder="请选择类型，支持多选和自定义输入"
              options={genreOptions}
              filterOption={(inputValue, option) =>
                option?.label?.toLowerCase().includes(inputValue.toLowerCase())
              }
              maxTagCount={3}
              style={{ width: '100%' }}
            />
          </Form.Item>
          <Form.Item label="简介" name="summary">
            <Input.TextArea rows={4} placeholder="请输入作品简介" />
          </Form.Item>
          <Form.Item
            label="每章目标字数"
            name="target_words_per_chapter"
            initialValue={2000}
            tooltip="AI 生成章节时会参考此字数，也可作为写作目标"
            rules={[{ required: true, message: '请设置目标字数' }]}
          >
            <InputNumber
              min={500}
              max={10000}
              step={500}
              style={{ width: '100%' }}
              placeholder="建议 2000-3000 字"
              addonAfter="字"
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default Dashboard
