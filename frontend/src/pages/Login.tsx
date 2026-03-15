import { Form, Input, Button, Card, message } from 'antd'
import { UserOutlined, LockOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { authApi } from '../services/api'
import { useAuthStore } from '../utils/store'

const Login = () => {
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()

  const onFinish = async (values: { username: string; password: string }) => {
    try {
      const response = await authApi.login(values)
      localStorage.setItem('token', response.data.access_token)
      message.success('登录成功')
      navigate('/dashboard')
    } catch (error: any) {
      message.error(error.response?.data?.detail || '登录失败')
    }
  }

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', background: '#f0f2f5' }}>
      <Card title="登录" style={{ width: 400 }}>
        <Form onFinish={onFinish} size="large">
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
    </div>
  )
}

export default Login
