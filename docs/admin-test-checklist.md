# 管理员权限测试清单

## 修复状态

✅ **问题 1 已修复：** 刷新页面后管理员页签消失
- 修改了 `frontend/src/utils/store.ts`
- 现在会从 JWT token 恢复用户信息

✅ **问题 2 已修复：** 管理员看不到别人的作品
- 运行了诊断脚本
- admin 用户的 is_admin = 1（正确）
- 数据库中有 6 个项目（testuser 5 个 + admin 1 个）

## 当前数据库状态

```
用户 (4 个):
  - testuser (ID: 1, 普通用户, 5 个项目)
  - testuser_new (ID: 2, 普通用户, 0 个项目)
  - admin (ID: 3, 管理员, 1 个项目)
  - regularuser (ID: 4, 普通用户, 0 个项目)

项目 (6 个):
  - 管理员的项目 (ID: 122, 所有者: admin)
  - 苍岚记 (ID: 3, 所有者: testuser)
  - 测试小说 (ID: 117, 所有者: testuser)
  - 测试小说 (ID: 118, 所有者: testuser)
  - 测试小说 (ID: 120, 所有者: testuser)
  - 测试小说 (ID: 121, 所有者: testuser)
```

## 测试步骤

### 第 1 步：清除浏览器缓存

在浏览器中按 F12 打开开发者工具，然后在控制台执行：

```javascript
localStorage.clear()
location.reload()
```

### 第 2 步：使用 admin 账号登录

1. 访问：`http://localhost:5173/login`
2. 点击管理员账号的"一键填入"按钮
   - 用户名：`admin`
   - 密码：`admin123`
3. 点击"登录"

### 第 3 步：验证管理员权限

登录成功后，检查以下内容：

#### ✅ 应该看到：
- [ ] 左侧菜单显示"管理员"选项
- [ ] Dashboard 显示 **6 个项目**（所有项目）
- [ ] 可以看到 testuser 创建的项目：
  - 苍岚记
  - 测试小说 (x4)
  - 管理员的项目

#### ❌ 如果只看到 1 个项目：
说明管理员权限没有生效。检查：
1. 浏览器控制台是否有错误
2. 打开 Network 标签，查看 `/api/projects/list` 请求
3. 查看响应中的 `total` 是否为 6
4. 查看后端日志，确认 `is_admin=1`

### 第 4 步：测试编辑其他用户的项目

1. 点击 testuser 创建的项目（如"苍岚记"）
2. 尝试编辑项目信息
3. 点击"保存"

#### ✅ 应该：
- 能成功打开项目详情页
- 能编辑并保存项目信息

### 第 5 步：测试普通用户权限

1. 点击右上角用户菜单
2. 点击"退出登录"
3. 使用 testuser 账号登录
   - 用户名：`testuser`
   - 密码：`password123`

#### ✅ 应该看到：
- [ ] 左侧菜单**没有**"管理员"选项
- [ ] Dashboard 只显示 **5 个项目**（testuser 自己的项目）
- [ ] 看不到 admin 创建的"管理员的项目"

### 第 6 步：测试普通用户无法访问管理员的项目

1. 在浏览器地址栏输入：
   ```
   http://localhost:5173/project/122
   ```
   （122 是 admin 创建的项目 ID）

2. 按 Enter 访问

#### ✅ 应该：
- 显示"无权限"错误
- 或者自动跳转回 Dashboard

## 调试技巧

### 查看 JWT Token 内容

在浏览器控制台执行：

```javascript
const token = localStorage.getItem('token')
const base64Url = token.split('.')[1]
const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
  return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
}).join(''))
console.log('JWT Payload:', JSON.parse(jsonPayload))
```

**admin 用户应该看到：**
```json
{
  "sub": "admin",
  "is_admin": 1,
  "exp": ...
}
```

**testuser 应该看到：**
```json
{
  "sub": "testuser",
  "is_admin": 0,
  "exp": ...
}
```

### 查看当前用户状态

在浏览器控制台执行：

```javascript
// 在 React DevTools 中查看 useAuthStore
// 或者在任何组件中：
import { useAuthStore } from './utils/store'
const authStore = useAuthStore.getState()
console.log('Current user:', authStore.user)
console.log('is_admin:', authStore.user?.is_admin)
```

### 查看 API 请求

1. 打开开发者工具 (F12)
2. 切换到 Network 标签
3. 刷新页面
4. 找到 `/api/projects/list` 请求
5. 点击查看响应

**管理员应该看到：**
```json
{
  "code": 200,
  "data": {
    "projects": [... 6 个项目 ...],
    "total": 6
  }
}
```

**普通用户应该看到：**
```json
{
  "code": 200,
  "data": {
    "projects": [... 5 个项目 ...],
    "total": 5
  }
}
```

## 常见问题

### Q1: 为什么还是只看到 1 个项目？

**可能原因：**
1. 浏览器缓存了旧的 token
2. 没有完全清除 localStorage

**解决方法：**
1. 完全关闭浏览器
2. 重新打开浏览器
3. 清除所有缓存和 Cookie
4. 重新登录

### Q2: 左侧菜单没有"管理员"选项？

**可能原因：**
1. 没有使用 admin 账号登录
2. JWT token 中的 is_admin 不是 1

**解决方法：**
1. 使用上述调试技巧查看 JWT token
2. 确认 `is_admin` 为 1
3. 如果不是，运行 `python diagnose_admin.py` 修复

### Q3: 刷新后管理员页签又消失了？

**可能原因：**
1. 没有重新启动前端服务
2. 浏览器缓存了旧的 JS 文件

**解决方法：**
1. 重启前端服务：`cd frontend && npm run dev`
2. 强制刷新浏览器：Ctrl + Shift + R
3. 清除浏览器缓存

## 成功标准

如果所有检查项都通过（打钩），说明管理员权限系统已经完全正常工作了！

## 下一步

如果测试通过，你可以：
1. ✅ 开始使用管理员账号管理所有用户的作品
2. ✅ 在管理面板中管理用户权限
3. ✅ 为其他用户创建项目并协助编辑
