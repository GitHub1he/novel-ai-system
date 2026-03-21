-- 小说AI生成与管理系统 - 数据库初始化脚本
-- 版本: 1.0
-- 说明: 创建所有表并插入默认测试数据

-- ============================================
-- 1. 用户表 (users)
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    avatar VARCHAR(500),
    preferred_genre VARCHAR(100),
    is_admin INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 2. 项目表 (projects)
-- ============================================
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    author VARCHAR(255) NOT NULL,
    genre VARCHAR(100) NOT NULL,
    tags TEXT,
    summary TEXT,
    target_readers VARCHAR(255),
    status VARCHAR(50) DEFAULT 'draft',
    default_pov VARCHAR(100),
    style VARCHAR(255),
    target_words_per_chapter INTEGER DEFAULT 2000,
    background_template TEXT,
    total_words INTEGER DEFAULT 0,
    total_chapters INTEGER DEFAULT 0,
    completion_rate INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 3. 人物表 (characters)
-- ============================================
CREATE TABLE IF NOT EXISTS characters (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    gender VARCHAR(50),
    age INTEGER,
    appearance TEXT,
    personality TEXT,
    background TEXT,
    relationships TEXT,
    role_type VARCHAR(100),
    importance INTEGER DEFAULT 1,
    avatar VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 4. 世界观设定表 (world_settings)
-- ============================================
CREATE TABLE IF NOT EXISTS world_settings (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    description TEXT,
    parent_id INTEGER REFERENCES world_settings(id) ON DELETE SET NULL,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 5. 章节表 (chapters)
-- ============================================
CREATE TABLE IF NOT EXISTS chapters (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    chapter_number INTEGER NOT NULL,
    content TEXT,
    summary TEXT,
    status VARCHAR(50) DEFAULT 'draft',
    word_count INTEGER DEFAULT 0,
    target_words INTEGER DEFAULT 2000,
    generation_count INTEGER DEFAULT 0,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, chapter_number)
);

-- ============================================
-- 6. 创建索引
-- ============================================

-- 用户表索引
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- 项目表索引
CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_genre ON projects(genre);

-- 人物表索引
CREATE INDEX IF NOT EXISTS idx_characters_project_id ON characters(project_id);
CREATE INDEX IF NOT EXISTS idx_characters_role_type ON characters(role_type);

-- 世界观设定索引
CREATE INDEX IF NOT EXISTS idx_world_settings_project_id ON world_settings(project_id);
CREATE INDEX IF NOT EXISTS idx_world_settings_category ON world_settings(category);

-- 章节表索引
CREATE INDEX IF NOT EXISTS idx_chapters_project_id ON chapters(project_id);
CREATE INDEX IF NOT EXISTS idx_chapters_status ON chapters(status);

-- ============================================
-- 7. 插入默认测试数据
-- ============================================

-- 注意：这里的密码是 'password123' 的 bcrypt 哈希值
-- 实际密码请使用后端工具生成
INSERT INTO users (email, username, hashed_password, preferred_genre, is_admin, is_active)
VALUES (
    'test@example.com',
    'testuser',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ND7Wq8To4cWq',
    '玄幻',
    0,
    1
) ON CONFLICT (email) DO NOTHING;

-- ============================================
-- 8. 创建视图（可选）
-- ============================================

-- 项目统计视图
CREATE OR REPLACE VIEW project_stats AS
SELECT
    p.id,
    p.title,
    p.user_id,
    COUNT(DISTINCT c.id) as chapter_count,
    COUNT(DISTINCT ch.id) as character_count,
    SUM(c.word_count) as total_words,
    p.created_at
FROM projects p
LEFT JOIN chapters c ON p.id = c.project_id
LEFT JOIN characters ch ON p.id = ch.project_id
GROUP BY p.id;

-- ============================================
-- 初始化完成
-- ============================================

-- 查看表结构
SELECT
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
    AND table_name IN ('users', 'projects', 'characters', 'world_settings', 'chapters')
ORDER BY table_name, ordinal_position;

-- 显示成功信息
SELECT 'Database initialization completed!' as status;
SELECT 'Test user created:' as info;
SELECT email, username FROM users WHERE email = 'test@example.com';
