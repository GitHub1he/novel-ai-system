# Claude AI 上下文提示

## 项目快速理解

这是一个**小说生成与管理系统**，核心功能是帮助作者：
1. 管理小说项目
2. 创作和管理章节
3. 管理人物设定
4. 管理世界观设定
5. AI辅助创作

## 技术架构

- **后端**: FastAPI + SQLAlchemy (Python)
- **前端**: React + TypeScript + Vite + Ant Design
- **通信**: RESTful API (JSON)

## 关键设计原则

1. **性能优化**: 列表接口不返回大字段（content、outline）
2. **按需加载**: 点击章节时才获取完整内容
3. **状态管理**: 章节有三种状态（草稿/修订中/已完成）
4. **统一响应**: 所有API返回 `{code, message, data}` 格式

## 最常用的文件

当用户说"章节相关"时，优先查看：
- `frontend/src/pages/ProjectDetail.tsx` (章节创作页面)
- `backend/app/api/chapters.py` (章节API)
- `frontend/src/services/api.ts` (API定义)

当用户说"人物相关"时，优先查看：
- `frontend/src/components/CharacterManagement.tsx`
- `backend/app/api/characters.py`

当用户说"世界观相关"时，优先查看：
- `frontend/src/components/WorldSettingManagement.tsx`
- `backend/app/api/world_settings.py`

## 常见问题模式

1. **"点击XX没反应"** → 检查事件处理函数是否绑定
2. **"报错"** → 检查前端语法、后端异常处理
3. **"样式不好看"** → 优化UI组件、添加Card、颜色编码
4. **"性能问题"** → 检查是否返回了不必要的大字段
5. **"中文输入问题"** → 使用TextArea而不是contentEditable

## 最新重要更新

- ✅ 章节列表API已优化，不返回content字段
- ✅ 章节详情按需加载
- ✅ 添加了状态切换功能
- ✅ 添加了返回列表按钮
- ✅ 修复了中文输入问题

## 待办事项

- AI生成功能未实现
- 章节导出功能未实现
- 自动保存功能未实现

---

**使用提示**：当用户提出新需求时，先查看 `PROJECT_STRUCTURE.md` 了解完整架构，再定位相关文件。