# Novel AI System - Frontend

AI小说生成与管理系统前端应用

## 技术栈

- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **UI组件**: Ant Design 5
- **富文本编辑器**: TipTap
- **路由**: React Router 6
- **状态管理**: Zustand
- **HTTP客户端**: Axios

## 快速开始

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

应用将在 http://localhost:5173 启动

### 3. 构建生产版本

```bash
npm run build
```

## 项目结构

```
frontend/
├── src/
│   ├── components/   # 可复用组件
│   ├── pages/        # 页面组件
│   ├── services/     # API服务
│   ├── types/        # TypeScript类型定义
│   ├── utils/        # 工具函数（状态管理等）
│   └── styles/       # 样式文件
├── index.html        # HTML入口
├── vite.config.ts    # Vite配置
└── package.json      # 依赖配置
```

## 功能模块

### 已实现

- 用户注册/登录
- 项目管理（创建、列表、查看）
- 基础布局框架
- API服务封装

### 待实现

- 富文本编辑器集成
- 章节管理
- AI内容生成
- 人物/世界观设定管理
- 版本管理
- 数据可视化

## 开发说明

### API配置

API代理配置在 `vite.config.ts`：

```typescript
server: {
  port: 5173,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    }
  }
}
```

### 状态管理

使用Zustand进行全局状态管理：

- `useAuthStore`: 用户认证状态
- `useProjectStore`: 项目状态

### 路由

- `/login`: 登录页
- `/register`: 注册页
- `/dashboard`: 工作台
- `/project/:id`: 项目详情

## 后续开发计划

- [ ] 集成TipTap富文本编辑器
- [ ] 实现章节创建和编辑
- [ ] 实现AI生成功能UI
- [ ] 添加人物管理页面
- [ ] 添加世界观设定页面
- [ ] 实现版本对比功能
- [ ] 添加数据统计图表
