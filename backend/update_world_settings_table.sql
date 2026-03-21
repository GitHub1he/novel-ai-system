-- 更新 world_settings 表 - 添加缺失的字段
ALTER TABLE world_settings ADD COLUMN IF NOT EXISTS setting_type VARCHAR(50);
ALTER TABLE world_settings ADD COLUMN IF NOT EXISTS attributes JSONB;
ALTER TABLE world_settings ADD COLUMN IF NOT EXISTS related_entities JSONB;
ALTER TABLE world_settings ADD COLUMN IF NOT EXISTS is_core_rule INTEGER DEFAULT 0;
ALTER TABLE world_settings ADD COLUMN IF NOT EXISTS image VARCHAR(500);
