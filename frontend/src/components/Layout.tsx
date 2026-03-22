import { Layout as AntLayout, Menu, Avatar, Dropdown, message } from 'antd'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { LogoutOutlined, UserOutlined, BookOutlined } from '@ant-design/icons'
import { useAuthStore } from '../utils/store'

const { Header, Sider, Content } = AntLayout

const Layout = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuthStore()

  const menuItems = [
    {
      key: '/dashboard',
      icon: <BookOutlined />,
      label: '工作台',
      onClick: () => navigate('/dashboard'),
    },
  ]

  // 如果是管理员，添加管理员菜单
  if (user?.is_admin) {
    menuItems.push({
      key: '/admin',
      icon: <UserOutlined />,
      label: '管理员',
      onClick: () => navigate('/admin'),
    })
  }

  const userMenuItems = [
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: () => {
        logout()
        message.success('已退出登录')
        navigate('/login')
      },
    },
  ]

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Sider theme="light" width={240}>
        <div style={{ padding: '16px', textAlign: 'center' }}>
          <h2 style={{ margin: 0 }}>小说AI系统</h2>
        </div>
        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
        />
      </Sider>
      <AntLayout>
        <Header style={{ background: '#fff', padding: '0 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div />
          <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
            <Avatar style={{ cursor: 'pointer' }} icon={<UserOutlined />} />
          </Dropdown>
        </Header>
        <Content style={{ margin: '24px', background: '#fff', padding: '24px', borderRadius: '8px' }}>
          <Outlet />
        </Content>
      </AntLayout>
    </AntLayout>
  )
}

export default Layout
