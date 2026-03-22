# 管理员权限调试指南

## 问题状态

✅ **后端查询逻辑正确** - 直接数据库查询能查到 6 个项目
✅ **普通用户权限正常** - 普通用户能看到自己的 5 个项目
❌ **管理员看不到其他用户的项目** - 需要调试

## 已添加的调试日志

我已经在前端代码中添加了详细的调试日志：

### 1. API 请求日志（`frontend/src/services/api.ts`）
```javascript
console.log('=== 发送 API 请求 ===')
console.log('URL:', config.url)
console.log('Method:', config.method)
console.log('Headers:', config.headers)
console.log('Token 存在:', !!token)
```

### 2. API 响应日志（`frontend/src/pages/Dashboard.tsx`）
```javascript
console.log('=== API 响应 ===')
console.log('完整响应:', response)
console.log('业务状态码:', response.data.code)
console.log('项目数量:', response.data.data?.total)
console.log('项目列表:', response.data.data?.projects)
```

## 调试步骤

### 第 1 步：清除浏览器缓存

1. 按 F12 打开开发者工具
2. 在控制台执行：
```javascript
localStorage.clear()
location.reload()
```

### 第 2 步：使用 admin 账号登录

1. 访问：`http://localhost:5173/login`
2. 用户名：`admin`
3. 密码：`admin123`
4. 点击"登录"

### 第 3 步：查看控制台日志

登录成功后，按 F12 打开开发者工具，切换到 Console 标签。

**你应该能看到类似这样的日志：**

```
=== 发送 API 请求 ===
URL: /projects/list
Method: get
Headers: {Authorization: "Bearer eyJhbGciOi...", ...}
Token 存在: true

=== API 响应 ===
完整响应: {data: {code: 200, data: {projects: [...], total: 6}}}
业务状态码: 200
项目数量: 6
项目列表: [{title: "苍岚记", ...}, {title: "测试小说", ...}, ...]
```

### 第 4 步：检查关键信息

#### ✅ 如果 `total: 6`
**说明：** 后端正常返回了所有 6 个项目
**下一步：** 检查页面显示是否正确

#### ❌ 如果 `total: 1`
**说明：** 后端只返回了 1 个项目（管理员自己的）
**可能原因：**
1. JWT token 中的 `is_admin` 不是 1
2. 后端 `get_current_user` 返回的用户 `is_admin` 不是 1
3. 后端查询逻辑有问题

**调试方法：**
```javascript
// 在控制台执行，查看 JWT 内容
const token = localStorage.getItem('token')
const payload = JSON.parse(atob(token.split('.')[1]))
console.log('JWT is_admin:', payload.is_admin)

// 应该显示：JWT is_admin: 1
```

### 第 5 步：检查后端日志

在运行后端的终端中，你应该能看到：

```
收到请求: GET /api/projects/list
...
获取项目列表成功: user_id=3, is_admin=1, count=6, total=6
```

**关键信息：**
- `user_id=3` - admin 的 ID
- `is_admin=1` - 管理员标识
- `count=6` - 返回的项目数
- `total=6` - 总项目数

### 第 6 步：检查 Network 标签

1. 按 F12 打开开发者工具
2. 切换到 Network 标签
3. 刷新页面
4. 找到 `/api/projects/list` 请求
5. 点击查看详细信息

**检查内容：**
- **Request Headers:** 应该有 `Authorization: Bearer eyJhbGci...`
- **Response:** 应该显示 `"total": 6`

## 可能的问题和解决方案

### 问题 1：前端缓存了旧的 token

**症状：** 控制台显示 `Token 存在: true`，但后端返回 401

**解决：**
```javascript
localStorage.clear()
location.reload()
```

### 问题 2：JWT token 中的 is_admin 不是 1

**症状：** 控制台显示 `JWT is_admin: 0` 或 `undefined`

**解决：**
1. 退出登录
2. 运行 `python diagnose_admin.py` 确认数据库中 admin.is_admin = 1
3. 重新登录

### 问题 3：后端返回的数据结构不对

**症状：** 后端日志显示 `count=6`，但前端显示 `total=1`

**解决：**
检查前端代码是否正确解析了响应：
```javascript
// 应该是这样：
setTotal(response.data.data.total)

// 而不是：
setTotal(response.data.total)
```

### 问题 4：后端查询逻辑有问题

**症状：** 后端日志显示 `is_admin=0` 或 `is_admin=False`

**解决：**
检查 `get_current_user` 函数，确保它返回了正确的用户对象：
```python
# 在 dependencies.py 中添加日志
logger.info(f"当前用户: {user.username}, is_admin={user.is_admin}")
```

## 快速验证方法

### 方法 1：使用浏览器控制台

1. 登录 admin 账号
2. 在控制台执行：
```javascript
// 检查 token
const token = localStorage.getItem('token')
console.log('Token:', token)

// 解码并查看
const payload = JSON.parse(atob(token.split('.')[1]))
console.log('JWT Payload:', payload)

// 调用 API
fetch('/api/projects/list', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
}).then(r => r.json()).then(data => {
  console.log('API Response:', data)
  console.log('Total:', data.data.total)
})
```

**预期输出：**
```json
{
  "code": 200,
  "data": {
    "projects": [... 6个项目 ...],
    "total": 6
  }
}
```

### 方法 2：查看调试页面

我创建了一个简单的调试页面：

1. 在浏览器中打开：`docs/debug-api.html`
2. 点击"登录"按钮
3. 点击"获取项目列表"按钮
4. 查看返回的项目数量

## 成功的标准

如果以下所有条件都满足，说明管理员权限已经正常工作：

- ✅ JWT token 中的 `is_admin` 为 1
- ✅ 后端日志显示 `is_admin=1`
- ✅ 后端日志显示 `count=6, total=6`
- ✅ 前端控制台显示 `total: 6`
- ✅ Dashboard 页面显示 6 个项目
- ✅ 刷新页面后仍然显示 6 个项目

## 下一步

请按照上述步骤操作，然后告诉我：

1. **控制台显示的 `total` 是多少？**
2. **后端日志显示的 `is_admin` 是多少？**
3. **是否有任何错误信息？**

根据这些信息，我可以精确定位问题所在并修复它。
