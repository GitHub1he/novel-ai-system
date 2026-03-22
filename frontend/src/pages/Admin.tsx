import { useEffect, useState } from 'react'
import { Card, Table, Button, Space, message, Modal, Statistic, Row, Col, Tag, Popconfirm, Switch } from 'antd'
import { UserOutlined, ProjectOutlined, BookOutlined, CheckCircleOutlined, StopOutlined } from '@ant-design/icons'
import { adminApi } from '../services/api'
import type { AdminUser, Project } from '../types'

const Admin = () => {
  const [users, setUsers] = useState<AdminUser[]>([])
  const [projects, setProjects] = useState<Project[]>([])
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState<'users' | 'projects' | 'stats'>('stats')

  // 获取统计信息
  const fetchStats = async () => {
    try {
      const response = await adminApi.getStats()
      if (response.data.code === 200) {
        setStats(response.data.data)
      }
    } catch (error: any) {
      if (error.response?.status === 403) {
        message.error('权限不足，需要管理员权限')
      } else {
        message.error('获取统计信息失败')
      }
    }
  }

  // 获取用户列表
  const fetchUsers = async () => {
    setLoading(true)
    try {
      const response = await adminApi.getUsers()
      if (response.data.code === 200) {
        setUsers(response.data.data.users)
      }
    } catch (error: any) {
      if (error.response?.status === 403) {
        message.error('权限不足，需要管理员权限')
      } else {
        message.error('获取用户列表失败')
      }
    } finally {
      setLoading(false)
    }
  }

  // 获取项目列表
  const fetchProjects = async () => {
    setLoading(true)
    try {
      const response = await adminApi.getAllProjects()
      if (response.data.code === 200) {
        setProjects(response.data.data.projects)
      }
    } catch (error: any) {
      if (error.response?.status === 403) {
        message.error('权限不足，需要管理员权限')
      } else {
        message.error('获取项目列表失败')
      }
    } finally {
      setLoading(false)
    }
  }

  // 切换管理员权限
  const handleToggleAdmin = async (userId: number, username: string) => {
    try {
      const response = await adminApi.toggleAdmin(userId)
      if (response.data.code === 200) {
        message.success(response.data.message)
        fetchUsers() // 刷新列表
      }
    } catch (error: any) {
      message.error('操作失败')
    }
  }

  // 切换用户状态
  const handleToggleActive = async (userId: number, username: string) => {
    try {
      const response = await adminApi.toggleActive(userId)
      if (response.data.code === 200) {
        message.success(response.data.message)
        fetchUsers() // 刷新列表
      }
    } catch (error: any) {
      message.error('操作失败')
    }
  }

  useEffect(() => {
    fetchStats()
  }, [])

  useEffect(() => {
    if (activeTab === 'users') {
      fetchUsers()
    } else if (activeTab === 'projects') {
      fetchProjects()
    }
  }, [activeTab])

  const userColumns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 60,
    },
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: '角色',
      dataIndex: 'is_admin',
      key: 'is_admin',
      render: (isAdmin: number) => (
        isAdmin ? <Tag color="red">管理员</Tag> : <Tag>普通用户</Tag>
      ),
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive: number) => (
        <Tag color={isActive ? 'green' : 'red'}>{isActive ? '正常' : '已禁用'}</Tag>
      ),
    },
    {
      title: '项目数',
      dataIndex: 'project_count',
      key: 'project_count',
      render: (count: number) => `${count} 个`,
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: AdminUser) => (
        <Space>
          <Popconfirm
            title="切换管理员权限"
            description={`确定要${record.is_admin ? '撤销' : '授予'} ${record.username} 的管理员权限吗？`}
            onConfirm={() => handleToggleAdmin(record.id, record.username)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" size="small">
              {record.is_admin ? '撤销管理员' : '设为管理员'}
            </Button>
          </Popconfirm>
          <Popconfirm
            title={record.is_active ? '禁用用户' : '启用用户'}
            description={`确定要${record.is_active ? '禁用' : '启用'}用户 ${record.username} 吗？`}
            onConfirm={() => handleToggleActive(record.id, record.username)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" danger size="small">
              {record.is_active ? '禁用' : '启用'}
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  const projectColumns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 60,
    },
    {
      title: '作品名',
      dataIndex: 'title',
      key: 'title',
    },
    {
      title: '作者',
      dataIndex: 'author',
      key: 'author',
    },
    {
      title: '所有者',
      dataIndex: 'owner_username',
      key: 'owner_username',
    },
    {
      title: '类型',
      dataIndex: 'genre',
      key: 'genre',
      render: (genre: string) => {
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
        }
        const info = statusMap[status] || { text: status, color: 'default' }
        return <Tag color={info.color}>{info.text}</Tag>
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
      <div style={{ marginBottom: 24 }}>
        <Space size="large">
          <Button
            type={activeTab === 'stats' ? 'primary' : 'default'}
            onClick={() => setActiveTab('stats')}
          >
            统计概览
          </Button>
          <Button
            type={activeTab === 'users' ? 'primary' : 'default'}
            onClick={() => setActiveTab('users')}
          >
            用户管理
          </Button>
          <Button
            type={activeTab === 'projects' ? 'primary' : 'default'}
            onClick={() => setActiveTab('projects')}
          >
            项目管理
          </Button>
        </Space>
      </div>

      {activeTab === 'stats' && stats && (
        <Row gutter={16}>
          <Col span={6}>
            <Card>
              <Statistic
                title="总用户数"
                value={stats.user_count}
                prefix={<UserOutlined />}
                valueStyle={{ color: '#3f8600' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="管理员数"
                value={stats.admin_count}
                prefix={<CheckCircleOutlined />}
                valueStyle={{ color: '#cf1322' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="总项目数"
                value={stats.project_count}
                prefix={<ProjectOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="总章节数"
                value={stats.chapter_count}
                prefix={<BookOutlined />}
                valueStyle={{ color: '#722ed1' }}
              />
            </Card>
          </Col>
        </Row>
      )}

      {activeTab === 'users' && (
        <Card title="用户列表" style={{ marginTop: 16 }}>
          <Table
            columns={userColumns}
            dataSource={users}
            rowKey="id"
            loading={loading}
            pagination={{ pageSize: 10 }}
          />
        </Card>
      )}

      {activeTab === 'projects' && (
        <Card title="项目列表" style={{ marginTop: 16 }}>
          <Table
            columns={projectColumns}
            dataSource={projects}
            rowKey="id"
            loading={loading}
            pagination={{ pageSize: 10 }}
          />
        </Card>
      )}
    </div>
  )
}

export default Admin
