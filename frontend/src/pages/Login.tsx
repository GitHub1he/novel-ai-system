import { Form, Input, Button, Card, message, Alert, Space } from 'antd'
import { UserOutlined, LockOutlined, ThunderboltOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { authApi } from '../services/api'
import { useAuthStore } from '../utils/store'

const Login = () => {
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()
  const [form] = Form.useForm()

  const onFinish = async (values: { username: string; password: string }) => {
    try {
      const response = await authApi.login(values)
      const token = response.data.access_token

      // 保存token
      localStorage.setItem('token', token)

      // 解码JWT获取用户信息
      const base64Url = token.split('.')[1]
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
      const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
      }).join(''))
      const payload = JSON.parse(jsonPayload)

      // 设置用户状态
      setAuth(
        {
          id: payload.sub || 0,  // 从token获取用户ID
          username: values.username,
          email: values.username + "@example.com",  // 临时邮箱
          is_admin: payload.is_admin || 0,  // 如果token中有is_admin
          is_active: 1,
          created_at: new Date().toISOString()
        },
        token
      )

      message.success('登录成功')
      navigate('/dashboard')
    } catch (error: any) {
      message.error(error.response?.data?.detail || '登录失败')
    }
  }

  const handleQuickFill = () => {
    form.setFieldsValue({
      username: 'testuser',
      password: 'password123'
    })
    message.success('已填入测试账号')
  }

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', background: '#f0f2f5' }}>
      <Space direction="vertical" size="large" style={{ width: 400 }}>
        <Card title="登录" style={{ width: 400 }}>
          <Form form={form} onFinish={onFinish} size="large">
            <Form.Item name="username" rules={[{ required: true, message: '请输入用户名' }]}>
              <Input prefix={<UserOutlined />} placeholder="用户名" />
            </Form.Item>
            <Form.Item name="password" rules={[{ required: true, message: '请输入密码' }]}>
              <Input.Password prefix={<LockOutlined />} placeholder="密码" />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit" block>
                登录
              </Button>
            </Form.Item>
            <div style={{ textAlign: 'center' }}>
              还没有账号？ <a onClick={() => navigate('/register')}>注册</a>
            </div>
          </Form>
        </Card>

        <Alert
          message="测试账号"
          description={
            <div>
              <p style={{ margin: '8px 0' }}>
                <strong>用户名：</strong>testuser
              </p>
              <p style={{ margin: '8px 0' }}>
                <strong>密码：</strong>password123
              </p>
              <Button
                type="primary"
                size="small"
                icon={<ThunderboltOutlined />}
                onClick={handleQuickFill}
                style={{ marginTop: '8px' }}
              >
                一键填入
              </Button>
            </div>
          }
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
        />

        <Alert
          message="管理员账号"
          description={
            <div>
              <p style={{ margin: '8px 0' }}>
                <strong>用户名：</strong>admin
              </p>
              <p style={{ margin: '8px 0' }}>
                <strong>密码：</strong>admin123
              </p>
              <Button
                type="primary"
                size="small"
                danger
                icon={<ThunderboltOutlined />}
                onClick={() => {
                  form.setFieldsValue({
                    username: 'admin',
                    password: 'admin123'
                  })
                  message.success('已填入管理员账号')
                }}
                style={{ marginTop: '8px' }}
              >
                一键填入
              </Button>
            </div>
          }
          type="warning"
          showIcon
        />
      </Space>
    </div>
  )
}

export default Login
