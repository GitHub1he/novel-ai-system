# 管理员权限实现总结

## 修改日期
2025-03-21

## 目标
为管理员账号提供对所有业务数据的完全访问权限（查看、编辑、删除所有用户的项目、章节、人物、世界观设定）。

## 修改的文件

### 1. backend/app/api/projects.py ✅
**修改内容：**
- 所有端点添加 `current_user: User = Depends(get_current_user)` 参数
- 使用条件查询：管理员可以查看/编辑/删除所有项目，普通用户只能访问自己的项目

**修改的端点：**
- `POST /projects/create` - 验证项目所有权，管理员可在任何项目中创建
- `GET /projects/list` - 管理员可查看所有项目，普通用户只看自己的
- `GET /projects/detail/{project_id}` - 管理员可查看任何项目详情
- `POST /projects/update/{project_id}` - 管理员可更新任何项目
- `POST /projects/del/{project_id}` - 管理员可删除任何项目

**权限检查模式：**
```python
# 列表查询
query = db.query(Project)
if not current_user.is_admin:
    query = query.filter(Project.user_id == current_user.id)

# 单个对象查询
query = db.query(Project).filter(Project.id == project_id)
if not current_user.is_admin:
    query = query.filter(Project.user_id == current_user.id)
project = query.first()
```

---

### 2. backend/app/api/chapters.py ✅
**修改内容：**
- 所有端点添加 `current_user: User = Depends(get_current_user)` 参数
- 添加 `HTTPException, status` 导入
- 章节属于项目，通过 `chapter.project.user_id` 验证所有权

**修改的端点：**
- `POST /chapters/` - 创建章节，检查项目所有权
- `GET /chapters/{chapter_id}` - 获取章节详情
- `PUT /chapters/{chapter_id}` - 更新章节
- `GET /chapters/list/{project_id}` - 获取章节列表，检查项目所有权
- `POST /chapters/{chapter_id}/generate` - AI生成内容
- `POST /chapters/generate` - 统一章节生成
- `POST /chapters/{chapter_id}/select-version` - 选择版本
- `GET /chapters/{chapter_id}/drafts` - 获取生成版本
- `DELETE /chapters/{chapter_id}` - 删除章节

**权限检查模式：**
```python
# 验证项目所有权（管理员可以访问所有项目）
if project.user_id != current_user.id and not current_user.is_admin:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="无权限访问该项目"
    )
```

---

### 3. backend/app/api/characters.py ✅
**修改内容：**
- 添加 `HTTPException, status` 和 `joinedload` 导入
- 添加 `Project` 模型导入
- 所有端点检查项目所有权，人物通过 `character.project.user_id` 验证

**修改的端点：**
- `POST /characters/create` - 创建人物，检查项目所有权
- `GET /characters/list/{project_id}` - 获取人物列表，检查项目所有权
- `GET /characters/detail/{character_id}` - 获取人物详情，使用 joinedload 预加载项目
- `POST /characters/update/{character_id}` - 更新人物
- `POST /characters/del/{character_id}` - 删除人物

**权限检查模式：**
```python
# 验证项目所有权（管理员可以在任何项目中创建人物）
project = db.query(Project).filter(Project.id == character.project_id).first()
if not project:
    raise NotFoundException("项目不存在")

if project.user_id != current_user.id and not current_user.is_admin:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="无权限在该项目中创建人物"
    )

# 对于详情/更新/删除，使用 joinedload 预加载
character = db.query(Character).options(
    joinedload(Character.project)
).filter(Character.id == character_id).first()

if character.project.user_id != current_user.id and not current_user.is_admin:
    raise HTTPException(...)
```

---

### 4. backend/app/api/world_settings.py ✅
**修改内容：**
- 添加 `HTTPException, status` 和 `joinedload` 导入
- 添加 `Project` 模型导入
- 所有端点检查项目所有权，世界观设定通过 `setting.project.user_id` 验证

**修改的端点：**
- `POST /world-settings/create` - 创建世界观设定，检查项目所有权
- `GET /world-settings/list/{project_id}` - 获取世界观设定列表
- `GET /world-settings/detail/{setting_id}` - 获取世界观设定详情
- `POST /world-settings/update/{setting_id}` - 更新世界观设定
- `POST /world-settings/del/{setting_id}` - 删除世界观设定

**权限检查模式：**
```python
# 验证项目所有权（管理员可以在任何项目中创建世界观设定）
project = db.query(Project).filter(Project.id == setting.project_id).first()
if not project:
    raise NotFoundException("项目不存在")

if project.user_id != current_user.id and not current_user.is_admin:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="无权限在该项目中创建世界观设定"
    )
```

---

## 权限验证规则总结

### 管理员（is_admin = 1）
- ✅ 可以查看所有用户的项目
- ✅ 可以在所有项目中创建章节、人物、世界观设定
- ✅ 可以编辑、删除任何用户创建的内容
- ✅ 可以访问管理面板（/admin）

### 普通用户（is_admin = 0）
- ✅ 只能查看自己的项目
- ✅ 只能在自己的项目中创建内容
- ✅ 只能编辑、删除自己创建的内容
- ❌ 无法访问管理面板（返回 403 Forbidden）

---

## JWT Token 结构

登录成功后，JWT token 包含：
```json
{
  "sub": "username",
  "is_admin": 1  // 1 表示管理员，0 表示普通用户
}
```

前端解码 token 获取用户信息：
```typescript
const payload = JSON.parse(atob(token.split('.')[1]))
setAuth({
  id: payload.sub,
  username: values.username,
  is_admin: payload.is_admin || 0,
  // ...
})
```

---

## 测试账号

### 管理员账号
- 用户名：`admin`
- 密码：`admin123`
- 权限：完全访问所有数据

### 测试账号
- 用户名：`testuser`
- 密码：`password123`
- 权限：只能访问自己的数据

---

## 如何测试

### 1. 测试管理员访问所有项目
```bash
# 使用管理员 token
curl -H "Authorization: Bearer <admin_token>" \
  http://localhost:8000/api/projects/list

# 预期：返回所有用户的项目
```

### 2. 测试普通用户只能看到自己的项目
```bash
# 使用普通用户 token
curl -H "Authorization: Bearer <user_token>" \
  http://localhost:8000/api/projects/list

# 预期：只返回该用户的项目
```

### 3. 测试管理员访问其他用户的章节
```bash
# 管理员访问其他用户项目的章节
curl -H "Authorization: Bearer <admin_token>" \
  http://localhost:8000/api/chapters/list/{other_user_project_id}

# 预期：成功返回章节列表
```

### 4. 测试普通用户无法访问其他用户的数据
```bash
# 普通用户尝试访问其他用户的项目
curl -H "Authorization: Bearer <user_token>" \
  http://localhost:8000/api/projects/detail/{other_user_project_id}

# 预期：403 Forbidden
```

---

## 安全注意事项

1. **所有端点都已认证**：所有业务 API 都需要通过 `get_current_user()` 依赖验证 JWT token
2. **管理员无法修改自己的权限**：在 `/admin/users/{user_id}/toggle-admin` 中有检查
3. **所有权验证**：所有修改/删除操作都验证用户是否拥有该资源（管理员除外）
4. **级联删除**：删除项目会级联删除相关的章节、人物、世界观设定

---

## 下一步

- [ ] 测试管理员权限是否正常工作
- [ ] 检查日志确认权限检查生效
- [ ] 考虑添加审计日志记录管理员操作
