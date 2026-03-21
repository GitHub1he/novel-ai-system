# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Novel AI System (小说AI生成与管理系统) is an AI-assisted novel creation platform that helps authors manage projects, characters, world-building settings, and chapters. The system uses AI (primarily ZhipuAI GLM-4) to generate content while maintaining narrative consistency.

**Tech Stack:**
- **Backend**: FastAPI (Python 3.10+) + PostgreSQL 15 + SQLAlchemy ORM
- **Frontend**: React 18 + TypeScript + Vite + Ant Design
- **AI Service**: ZhipuAI GLM-4 (supports OpenAI-compatible API switching)

## Common Commands

### Backend Development
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Initialize database (creates tables and test user)
python init_db.py

# Start development server (auto-reload)
python main.py
# OR: uvicorn main:app --reload

# Reset database (drop and recreate)
docker-compose exec postgres psql -U novel_ai_user -d novel_ai_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
```

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Type check
tsc --noEmit

# Build for production
npm run build
```

### Database (Docker)
```bash
# Start PostgreSQL
docker-compose up -d postgres

# Stop database
docker-compose stop postgres

# View logs
docker-compose logs postgres

# Connect to database
docker-compose exec postgres psql -U novel_ai_user -d novel_ai_db
```

## Architecture Overview

### Backend Structure (`backend/app/`)
- **`api/`**: Route handlers (auth, projects, chapters, characters, world_settings, plot_nodes)
- **`core/`**: Configuration, database connection, exception handlers, logging
- **`models/`**: SQLAlchemy ORM models (User, Project, Chapter, Character, WorldSetting, PlotNode)
- **`schemas/`**: Pydantic models for request/response validation
- **`services/`**: Business logic (AI generation service)

### Frontend Structure (`frontend/src/`)
- **`pages/`**: Main pages (Dashboard, ProjectDetail, Login, Register)
- **`components/`**: Feature components (CharacterManagement, WorldSettingManagement, etc.)
- **`services/api.ts`**: Axios API client with interceptors for auth and error handling
- **`types/index.ts`**: TypeScript type definitions

### Key Architecture Patterns

**1. List/Detail Pattern for Performance**
List endpoints (e.g., `/chapters/list/{project_id}`) exclude large fields like `content` and `outline`. Details are fetched on-demand via separate endpoints (e.g., `/chapters/{id}`). This prevents loading massive content when viewing lists.

**2. Unified API Response Format**
All API responses follow this structure:
```json
{
  "code": 200,
  "message": "操作成功",
  "data": { ... }
}
```

**3. AI Service Integration**
The `AIService` class (`backend/app/services/ai_service.py`) integrates with ZhipuAI GLM-4 but supports any OpenAI-compatible API. It builds context from project settings, characters, and world-building to generate content with consistency.

**4. Exception Handling**
Custom exceptions in `backend/app/core/exception_handler.py`:
- `NotFoundException`: Resource not found (404)
- `BusinessException`: Business logic errors (400)
- `ValidationException`: Validation errors (422)

## Configuration

### Backend Environment Variables (`.env`)
Required variables in `backend/.env`:
```env
DATABASE_URL=postgresql://novel_ai_user:novel_ai_password@localhost:5432/novel_ai_db
ZHIPUAI_API_KEY=your-zhipuai-api-key  # Get from https://open.bigmodel.cn/usercenter/apikeys
OPENAI_API_BASE=https://open.bigmodel.cn/api/paas/v4/
AI_MODEL=glm-4-flash  # Options: glm-4-flash, glm-4, glm-4-plus
SECRET_KEY=your-secret-key-change-in-production
```

### Frontend Proxy Configuration
Vite proxy forwards `/api` requests to backend at `http://127.0.0.1:8000` (configured in `frontend/vite.config.ts`).

## Data Model Relationships

```
User (用户)
  └── 1:N Project (项目)
       ├── 1:N Chapter (章节)
       ├── 1:N Character (人物)
       ├── 1:N WorldSetting (世界观设定)
       └── 1:N PlotNode (情节节点)
```

**Key Models:**
- **Project**: Title, genre, style, summary, target word count, status
- **Chapter**: Chapter number, title, content (large text), outline (large text), status (draft/revising/completed), word count
- **Character**: Name, role type (protagonist/antagonist/supporting/minor), character arc (initial→turning point→final), voice style, sample dialogue
- **WorldSetting**: Type (era/region/rules/culture/power system/location/faction/item/event), core rule flag, related entities

## API Endpoints Reference

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login (returns JWT token)

### Projects
- `GET /api/projects/list` - List all projects
- `GET /api/projects/detail/{id}` - Get project details
- `POST /api/projects/create` - Create project
- `POST /api/projects/update/{id}` - Update project
- `POST /api/projects/del/{id}` - Delete project

### Chapters
- `GET /api/chapters/list/{project_id}` - List chapters (excludes `content` field)
- `GET /api/chapters/{id}` - Get chapter details (includes `content`)
- `POST /api/chapters/` - Create chapter (auto-calculates chapter_number)
- `PUT /api/chapters/{id}` - Update chapter
- `POST /api/chapters/{id}/generate` - AI generate content

### Characters
- `GET /api/characters/list/{project_id}` - List characters
- `GET /api/characters/detail/{id}` - Get character details
- `POST /api/characters/create` - Create character
- `POST /api/characters/update/{id}` - Update character
- `POST /api/characters/del/{id}` - Delete character

### World Settings
- `GET /api/world-settings/list/{project_id}` - List world settings
- `GET /api/world-settings/detail/{id}` - Get world setting details
- `POST /api/world-settings/create` - Create world setting
- `POST /api/world-settings/update/{id}` - Update world setting
- `POST /api/world-settings/del/{id}` - Delete world setting

## Important Development Notes

1. **Large Text Fields**: When working with chapters, always use list endpoints for browsing and only fetch individual chapter details when needed to avoid performance issues.

2. **AI Model Selection**: Default is `glm-4-flash` for speed and cost-efficiency. Use `glm-4-plus` for complex scenes requiring higher quality.

3. **Database Initialization**: The `init_db.py` script creates a test user (`test@example.com` / `password123`). Use this for development instead of registering new accounts each time.

4. **CORS Configuration**: Backend accepts requests from `http://localhost:3000` and `http://localhost:5173`. Update `BACKEND_CORS_ORIGINS` in `.env` if using different ports.

5. **Frontend State Management**: The main state is in `ProjectDetail.tsx` - manages `project`, `chapters`, `currentChapter`, and `loadingChapter` states. Follow this pattern for new features.

6. **Error Handling**: Frontend uses Ant Design's `message` component for notifications (`message.success()`, `message.error()`). Backend logs all operations using the configured logger.

## Test Credentials
- Email: `test@example.com`
- Username: `testuser`
- Password: `password123`

## Service URLs
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs
- Health Check: http://localhost:8000/health