# 统一权限管理系统重构指南

## 背景

当前实现在每个 API 接口中都重复编写权限检查代码，存在以下问题：
1. **代码重复**：每个接口都有 5-10 行相同的权限检查逻辑
2. **维护困难**：修改权限规则需要改动所有接口
3. **容易遗漏**：新增接口时可能忘记加权限检查
4. **性能问题**：重复查询数据库（如先查章节，再查项目）

## 解决方案：统一权限检查依赖

使用 FastAPI 的依赖注入功能，创建统一的权限检查函数，类似 Spring AOP 的切面思想。

## 核心文件

**`backend/app/core/permissions.py`** - 统一权限检查函数库

### 提供的函数

#### 1. `get_project` - 读取项目（管理员可访问）
```python
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Project:
    """管理员可访问任何项目，普通用户只能访问自己的项目"""
```

#### 2. `require_project` - 要求项目所有权（用于修改操作）
```python
def require_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Project:
    """管理员可修改任何项目，普通用户只能修改自己的项目"""
```

#### 3. `get_chapter` - 读取章节（通过项目检查权限）
```python
def get_chapter(
    chapter_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Chapter:
    """自动通过 chapter.project_id 检查项目权限，并预加载 project 对象"""
```

#### 4. `require_chapter` - 要求章节所有权（用于修改操作）
```python
def require_chapter(...) -> Chapter:
    """要求项目所有权，用于更新、删除操作"""
```

#### 5. `get_character` / `require_character` - 人物权限检查
```python
def get_character(...) -> Character:
    """通过 character.project_id 检查项目权限"""
```

#### 6. `get_world_setting` / `require_world_setting` - 世界观权限检查
```python
def get_world_setting(...) -> WorldSetting:
    """通过 setting.project_id 检查项目权限"""
```

---

## 重构步骤

### 步骤 1：在接口中导入权限函数

```python
from app.core.permissions import get_project, require_project, get_chapter, require_chapter
```

### 步骤 2：删除接口中的权限检查代码

**重构前：**
```python
@router.get("/detail/{project_id}")
def get_project_detail(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 查询项目
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise NotFoundException("项目不存在")

    # 权限检查（删除这些代码！）
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限访问该项目"
        )

    # 业务逻辑
    return {"code": 200, "data": project}
```

**重构后：**
```python
@router.get("/detail/{project_id}")
def get_project_detail(
    project: Project = Depends(get_project)  # 一行搞定！
):
    # 业务逻辑（权限已检查，直接使用 project）
    return {"code": 200, "data": project}
```

### 步骤 3：处理列表查询

列表查询需要先检查项目权限，再查询列表：

**重构前：**
```python
@router.get("/list/{project_id}")
def list_chapters(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 手动检查项目权限
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise NotFoundException("项目不存在")
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="无权限")

    # 查询章节列表
    chapters = db.query(Chapter).filter(
        Chapter.project_id == project_id
    ).all()

    return {"code": 200, "data": {"chapters": chapters}}
```

**重构后：**
```python
@router.get("/list/{project_id}")
def list_chapters(
    project_id: int,
    project: Project = Depends(get_project),  # 自动检查项目权限
    db: Session = Depends(get_db)
):
    # 直接查询章节列表（权限已检查）
    chapters = db.query(Chapter).filter(
        Chapter.project_id == project_id
    ).all()

    return {"code": 200, "data": {"chapters": chapters}}
```

### 步骤 4：处理创建操作

创建操作需要检查项目所有权：

**重构前：**
```python
@router.post("/")
def create_chapter(
    chapter_data: ChapterCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 手动检查项目权限
    project = db.query(Project).filter(Project.id == chapter_data.project_id).first()
    if not project:
        raise NotFoundException("项目不存在")
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="无权限")

    # 创建章节
    chapter = Chapter(**chapter_data.model_dump())
    db.add(chapter)
    db.commit()

    return {"code": 200, "data": chapter}
```

**重构后：**
```python
@router.post("/")
def create_chapter(
    chapter_data: ChapterCreate,
    project: Project = Depends(require_project),  # 要求项目所有权
    db: Session = Depends(get_db)
):
    # 创建章节（权限已检查）
    chapter = Chapter(**chapter_data.model_dump())
    db.add(chapter)
    db.commit()

    return {"code": 200, "data": chapter}
```

### 步骤 5：处理更新/删除操作

更新/删除操作使用 `require_*` 函数：

**重构前：**
```python
@router.put("/{chapter_id}")
def update_chapter(
    chapter_id: int,
    chapter_update: ChapterUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 查询章节
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise NotFoundException("章节不存在")

    # 手动检查项目权限
    if chapter.project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="无权限")

    # 更新章节
    update_data = chapter_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(chapter, field, value)
    db.commit()

    return {"code": 200, "data": chapter}
```

**重构后：**
```python
@router.put("/{chapter_id}")
def update_chapter(
    chapter_id: int,
    chapter_update: ChapterUpdate,
    chapter: Chapter = Depends(require_chapter),  # 自动检查权限！
    db: Session = Depends(get_db)
):
    # 更新章节（权限已检查，chapter.project 已预加载）
    update_data = chapter_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(chapter, field, value)
    db.commit()

    return {"code": 200, "data": chapter}
```

---

## 重构优先级

### 高优先级（建议立即重构）
- ✅ `backend/app/api/projects.py` - 项目接口（最常用）
- ✅ `backend/app/api/chapters.py` - 章节接口

### 中优先级
- 📋 `backend/app/api/characters.py` - 人物接口
- 📋 `backend/app/api/world_settings.py` - 世界观接口

### 低优先级
- 📋 `backend/app/api/plot_nodes.py` - 情节节点接口（如果有的话）

---

## 性能优化

### 优化 1：预加载关联对象

权限检查函数会自动预加载关联对象，避免重复查询：

```python
# 重构后：chapter.project 已预加载
def update_chapter(
    chapter: Chapter = Depends(require_chapter)  # 自动预加载 project
):
    # 直接使用，无额外查询
    project_title = chapter.project.title  # 无需再次查询数据库
```

### 优化 2：减少数据库查询

**重构前：** 每个接口 2 次查询
```python
# 查询 1：获取章节
chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
# 查询 2：获取项目（检查权限）
project = db.query(Project).filter(Project.id == chapter.project_id).first()
```

**重构后：** 每个接口 1 次查询（权限函数内部）
```python
chapter: Chapter = Depends(require_chapter)  # 内部优化查询，一次获取
```

---

## 测试检查清单

重构后需要测试以下场景：

### 1. 管理员访问（admin / admin123）
- [ ] 可以查看所有用户的项目
- [ ] 可以在任何项目中创建章节、人物、世界观
- [ ] 可以编辑、删除任何用户的内容
- [ ] 可以访问管理面板

### 2. 普通用户访问（testuser / password123）
- [ ] 只能查看自己的项目
- [ ] 只能在自己的项目中创建内容
- [ ] 只能编辑、删除自己的内容
- [ ] 无法访问其他用户的内容（返回 403）

### 3. 边界情况
- [ ] 访问不存在的资源（返回 404）
- [ ] 未登录访问（返回 401）
- [ ] Token 过期访问（返回 401）

---

## 代码对比总结

### 代码量减少

| 类型 | 重构前 | 重构后 | 减少 |
|------|--------|--------|------|
| **获取资源** | ~15 行 | ~5 行 | **-67%** |
| **列表查询** | ~20 行 | ~10 行 | **-50%** |
| **创建资源** | ~25 行 | ~12 行 | **-52%** |
| **更新/删除** | ~25 行 | ~12 行 | **-52%** |

### 维护性提升

| 指标 | 重构前 | 重构后 |
|------|--------|--------|
| **权限规则修改** | 需改所有接口 | 只改 permissions.py |
| **新增接口** | 容易遗漏权限检查 | 无法遗漏（依赖注入） |
| **代码重复** | 每个接口重复 | 零重复 |
| **测试复杂度** | 需测试每个接口 | 只测试权限函数 |

---

## 常见问题

### Q1: 如何处理特殊的权限规则？

**A:** 在 `permissions.py` 中添加新的权限检查函数：

```python
def check_published_project_access(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Project:
    """已发布的项目所有人可见"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise NotFoundException("项目不存在")

    # 已发布的项目所有人可见
    if project.is_published:
        return project

    # 未发布的需要所有权或管理员
    if project.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="无权限")

    return project
```

### Q2: 如何处理批量操作的权限检查？

**A:** 在循环前统一检查一次权限：

```python
@router.post("/batch-delete")
def batch_delete_chapters(
    chapter_ids: List[int],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 先检查所有章节是否属于同一项目
    chapters = db.query(Chapter).filter(Chapter.id.in_(chapter_ids)).all()
    project_ids = set(c.project_id for c in chapters)

    if len(project_ids) > 1:
        raise BusinessException("不能删除不同项目的章节")

    # 检查项目权限（只需一次）
    project = require_project(project_ids.pop(), current_user, db)

    # 批量删除
    db.query(Chapter).filter(Chapter.id.in_(chapter_ids)).delete(
        synchronize_session=False
    )
    db.commit()

    return {"code": 200, "message": f"删除了 {len(chapter_ids)} 个章节"}
```

### Q3: 权限检查会影响性能吗？

**A:** 不会，反而会提升性能：
1. 权限函数内部使用优化的查询（如 joinedload）
2. 预加载关联对象，避免重复查询
3. 减少代码执行路径

---

## 总结

使用统一权限检查依赖后：
- ✅ 代码量减少 50-67%
- ✅ 零重复代码
- ✅ 不会遗漏权限检查
- ✅ 修改权限规则只需改一个文件
- ✅ 更容易测试和维护
- ✅ 性能提升（减少重复查询）

**推荐立即开始重构！**
