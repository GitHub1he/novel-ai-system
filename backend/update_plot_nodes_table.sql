-- 添加情节节点表
CREATE TABLE IF NOT EXISTS plot_nodes (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    chapter_id INTEGER REFERENCES chapters(id) ON DELETE SET NULL,
    parent_plot_id INTEGER REFERENCES plot_nodes(id) ON DELETE SET NULL,

    -- 基本信息
    title VARCHAR(255) NOT NULL,
    description TEXT,
    plot_type VARCHAR(50) DEFAULT 'other',
    importance VARCHAR(50) DEFAULT 'main',

    -- 关联信息
    related_characters TEXT,
    related_locations TEXT,
    related_world_settings TEXT,

    -- 情节内容
    conflict_points TEXT,
    theme_tags TEXT,

    -- 结构信息
    sequence_number INTEGER DEFAULT 0,

    -- 状态
    is_completed INTEGER DEFAULT 0,

    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_plot_nodes_project_id ON plot_nodes(project_id);
CREATE INDEX IF NOT EXISTS idx_plot_nodes_chapter_id ON plot_nodes(chapter_id);
CREATE INDEX IF NOT EXISTS idx_plot_nodes_parent_plot_id ON plot_nodes(parent_plot_id);
CREATE INDEX IF NOT EXISTS idx_plot_nodes_sequence ON plot_nodes(sequence_number);
CREATE INDEX IF NOT EXISTS idx_plot_nodes_plot_type ON plot_nodes(plot_type);
CREATE INDEX IF NOT EXISTS idx_plot_nodes_importance ON plot_nodes(importance);

-- 添加项目表的文风相关字段
ALTER TABLE projects ADD COLUMN IF NOT EXISTS style_keywords TEXT;
ALTER TABLE projects ADD COLUMN IF NOT EXISTS language_style VARCHAR(50);
ALTER TABLE projects ADD COLUMN IF NOT EXISTS sensory_focus TEXT;
ALTER TABLE projects ADD COLUMN IF NOT EXISTS style_intensity INTEGER DEFAULT 70;

-- 添加注释
COMMENT ON TABLE plot_nodes IS '情节节点表';
COMMENT ON COLUMN plot_nodes.plot_type IS '情节类型：meeting/betrayal/reconciliation/conflict/revelation/transformation/climax/resolution/other';
COMMENT ON COLUMN plot_nodes.importance IS '重要程度：main/branch/background';
COMMENT ON COLUMN plot_nodes.sequence_number IS '顺序号，用于排序';
COMMENT ON COLUMN plot_nodes.related_characters IS '关联人物ID列表，JSON数组格式';
COMMENT ON COLUMN plot_nodes.related_locations IS '关联地点ID列表，JSON数组格式';
COMMENT ON COLUMN plot_nodes.related_world_settings IS '关联世界观ID列表，JSON数组格式';
COMMENT ON COLUMN plot_nodes.conflict_points IS '冲突点描述';
COMMENT ON COLUMN plot_nodes.theme_tags IS '主题标签，JSON数组格式';
COMMENT ON COLUMN plot_nodes.is_completed IS '是否完成：0=未完成，1=已完成';

COMMENT ON COLUMN projects.style_keywords IS '文风关键词，JSON数组格式';
COMMENT ON COLUMN projects.language_style IS '语言风格：concise/flowery/colloquial/formal';
COMMENT ON COLUMN projects.sensory_focus IS '感官重点，JSON数组格式';
COMMENT ON COLUMN projects.style_intensity IS '风格匹配度(0-100)';
