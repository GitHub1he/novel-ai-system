# 管理员权限问题修复指南

## 问题描述

1. ✅ **已修复：** 刷新页面后管理员页签消失
2. 🔧 **待修复：** 管理员看不到别人创建的作品

## 修复步骤

### 步骤 1：运行诊断和修复脚本

```bash
cd backend
python diagnose_admin.py
```

这个脚本会：
- ✅ 检查 admin 用户是否存在
- ✅ 检查 admin 用户的 is_admin 是否为 1
- ✅ 如果不存在，创建 admin 用户
- ✅ 如果权限不对，修复权限
- ✅ 创建测试用户 testuser
- ✅ 为两个用户创建测试项目
- ✅ 显示数据库统计信息

### 步骤 2：验证修复结果

运行脚本后，你应该看到类似这样的输出：

```
======================================================================
管理员权限诊断和修复
======================================================================

[1] 检查 admin 用户...
  ✓ admin 用户存在 (ID: 1)
  ✓ admin 用户的 is_admin = 1 (正确)

[2] 检查 testuser 用户...
  ✓ testuser 用户存在 (ID: 2)

[3] 创建测试项目...
  ✓ testuser 已有 1 个项目
  ✓ admin 已有 1 个项目

[4] 数据库统计...

  所有用户 (2 个):
    - admin (ID: 1, 管理员, 1 个项目)
    - testuser (ID: 2, 普通用户, 1 个项目)

  所有项目 (2 个):
    - 测试用户的项目1 (ID: 1, 所有者: testuser)
    - 管理员的项目 (ID: 2, 所有者: admin)

[5] 测试权限检查...
  admin.is_admin = 1
  testuser.is_admin = 0
  ✅ admin 用户权限正确

======================================================================
诊断完成！
======================================================================

📝 测试账号：
   管理员: admin / admin123 (ID: 1)
   普通用户: testuser / password123 (ID: 2)

📊 项目统计：
   总用户数: 2
   总项目数: 2
   testuser 项目数: 1
   admin 项目数: 1

🔍 测试步骤：
   1. 使用 admin 账号登录
   2. 查看 Dashboard，应该能看到所有项目（包括 testuser 的项目）
   3. 点击 testuser 的项目，应该能查看和编辑
   4. 退出登录
   5. 使用 testuser 账号登录
   6. 查看 Dashboard，应该只能看到自己的项目
   7. 尝试访问 admin 的项目（应该显示无权限）

======================================================================
```

### 步骤 3：清除浏览器缓存并重新登录

```bash
# 在浏览器中：
1. 打开开发者工具 (F12)
2. 进入 Application 标签
3. 点击 Local Storage
4. 删除 token
5. 刷新页面
```

或者直接在浏览器控制台执行：
```javascript
localStorage.clear()
location.reload()
```

### 步骤 4：使用 admin 账号登录

1. 访问：`http://localhost:5173/login`
2. 用户名：`admin`
3. 密码：`admin123`
4. 点击"登录"

### 步骤 5：验证管理员权限

登录成功后，你应该看到：

✅ **左侧菜单显示"管理员"选项**
✅ **Dashboard 显示所有项目**（包括 testuser 创建的项目）
✅ **可以点击并编辑其他用户的项目**

### 步骤 6：测试普通用户权限

1. 点击右上角用户菜单
2. 点击"退出登录"
3. 使用 testuser / password123 登录
4. 验证只能看到自己的项目

## 已修复的问题

### 问题 1：刷新页面后管理员页签消失 ✅

**原因：** `useAuthStore` 没有从 localStorage 的 token 中恢复用户信息

**修复：** 修改 `frontend/src/utils/store.ts`，从 JWT token 解码并恢复用户信息

```typescript
export const useAuthStore = create<AuthState>((set) => {
  // 从 localStorage 恢复用户信息
  const token = localStorage.getItem('token')
  let user = null

  if (token) {
    try {
      // 解码 JWT token 获取用户信息
      const base64Url = token.split('.')[1]
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
      const jsonPayload = decodeURIComponent(atob(base64)...)
      const payload = JSON.parse(jsonPayload)

      user = {
        id: payload.sub || 0,
        username: payload.sub,
        email: payload.sub + "@example.com",
        is_admin: payload.is_admin || 0,  // 关键：恢复 is_admin
        is_active: 1,
        created_at: new Date().toISOString()
      }
    } catch (error) {
      console.error('Failed to decode token:', error)
      localStorage.removeItem('token')
    }
  }

  return {
    user,
    token,
    setAuth: (user, token) => {
      localStorage.setItem('token', token)
      set({ user, token })
    },
    logout: () => {
      localStorage.removeItem('token')
      set({ user: null, token: null })
    },
  }
})
```

### 问题 2：管理员看不到别人创建的作品 🔧

**可能原因：**
1. 数据库中 admin 用户的 is_admin 不是 1
2. 数据库中没有其他用户创建的项目

**修复方法：**
运行 `python diagnose_admin.py` 诊断和修复

## 调试技巧

### 1. 检查 JWT Token 内容

在浏览器控制台执行：
```javascript
const token = localStorage.getItem('token')
const base64Url = token.split('.')[1]
const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
  return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
}).join(''))
const payload = JSON.parse(jsonPayload)
console.log('JWT Payload:', payload)
console.log('is_admin:', payload.is_admin)
```

预期输出：
```javascript
{
  "sub": "admin",
  "is_admin": 1,  // 必须是 1
  "exp": ...
}
```

### 2. 检查用户状态

在浏览器控制台执行：
```javascript
// 检查 Zustand store
import useAuthStore from './src/utils/store'
const authStore = useAuthStore.getState()
console.log('Current user:', authStore.user)
console.log('is_admin:', authStore.user?.is_admin)
```

预期输出：
```javascript
{
  id: 1,
  username: "admin",
  email: "admin@example.com",
  is_admin: 1,  // 必须是 1
  is_active: 1,
  ...
}
```

### 3. 检查 API 响应

在浏览器开发者工具的 Network 标签中：
1. 找到 `/api/projects/list` 请求
2. 查看响应内容

管理员应该看到：
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "projects": [
      { "id": 1, "title": "测试用户的项目1", "user_id": 2, ... },
      { "id": 2, "title": "管理员的项目", "user_id": 1, ... }
    ],
    "total": 2
  }
}
```

普通用户应该看到：
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "projects": [
      { "id": 1, "title": "测试用户的项目1", "user_id": 2, ... }
    ],
    "total": 1
  }
}
```

### 4. 查看后端日志

后端会打印权限检查日志：
```
获取项目列表成功: user_id=1, is_admin=1, count=2, total=2
```

如果 `is_admin=0`，说明数据库中的权限设置有问题。

## 常见问题

### Q1: 运行诊断脚本后还是看不到别人的项目？

**A:** 检查以下几点：
1. 确认使用 admin 账号登录（不是 testuser）
2. 清除浏览器缓存和 localStorage
3. 检查浏览器控制台是否有错误
4. 查看后端日志，确认 `is_admin=1`

### Q2: 登录后显示"权限不足"？

**A:** 可能原因：
1. JWT token 过期，重新登录
2. 数据库中 is_admin 不是 1，运行诊断脚本修复

### Q3: 刷新页面后还是看不到管理员页签？

**A:**
1. 确认已经修改了 `frontend/src/utils/store.ts`
2. 重启前端服务：`cd frontend && npm run dev`
3. 清除浏览器缓存
4. 重新登录

### Q4: 如何手动创建管理员账号？

**A:** 运行：
```bash
cd backend
python create_admin.py --username admin --email admin@example.com --password admin123
```

## 文件修改清单

### 已修改的文件
1. ✅ `frontend/src/utils/store.ts` - 从 JWT token 恢复用户信息
2. ✅ `backend/diagnose_admin.py` - 新建诊断和修复脚本

### 已创建的文件
1. ✅ `docs/fix-admin-permissions.md` - 本文档

## 总结

通过运行诊断脚本 `python diagnose_admin.py`，你可以：
- ✅ 自动创建或修复 admin 用户
- ✅ 自动创建测试用户和项目
- ✅ 验证权限设置是否正确
- ✅ 获得详细的调试信息

如果问题依然存在，请提供以下信息：
1. 诊断脚本的输出
2. 浏览器控制台的错误信息
3. 后端日志
4. JWT token 的内容（使用上述调试技巧查看）
