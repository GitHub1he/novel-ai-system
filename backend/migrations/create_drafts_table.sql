-- 创建内容生成草稿表
CREATE TABLE IF NOT EXISTS content_generation_drafts (
    id SERIAL PRIMARY KEY,
    chapter_id INTEGER NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    version_id VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    word_count INTEGER DEFAULT 0,
    summary TEXT,
    is_selected BOOLEAN DEFAULT FALSE,
    generation_mode VARCHAR(50),
    temperature VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(chapter_id, version_id)
);

-- 创建索引以提升查询性能
CREATE INDEX IF NOT EXISTS idx_drafts_chapter ON content_generation_drafts(chapter_id);
CREATE INDEX IF NOT EXISTS idx_drafts_selected ON content_generation_drafts(is_selected);
CREATE INDEX IF NOT EXISTS idx_drafts_created ON content_generation_drafts(created_at);

-- 添加注释
COMMENT ON TABLE content_generation_drafts IS '内容生成草稿表，保存AI生成的多个版本供用户选择';
COMMENT ON COLUMN content_generation_drafts.version_id IS '版本标识，如v1, v2, v3';
COMMENT ON COLUMN content_generation_drafts.is_selected IS '用户是否选中此版本作为正式内容';
