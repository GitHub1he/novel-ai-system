-- 更新 characters 表 - 添加人物弧光和语言风格的 JSONB 字段
ALTER TABLE characters ADD COLUMN IF NOT EXISTS character_arcs JSONB;
ALTER TABLE characters ADD COLUMN IF NOT EXISTS voice_styles JSONB;

-- 可选：迁移现有数据到新字段（根据需要执行）
-- UPDATE characters
-- SET character_arcs = ARRAY[
--   jsonb_build_object(
--     'period', '全篇',
--     'event', COALESCE(turning_point, '主线剧情'),
--     'before', COALESCE(initial_state, ''),
--     'after', COALESce(final_state, '')
--   )
-- ]::jsonb
-- WHERE initial_state IS NOT NULL OR turning_point IS NOT NULL OR final_state IS NOT NULL;

-- UPDATE characters
-- SET voice_styles = ARRAY[
--   jsonb_build_object(
--     'target', '通用',
--     'scenario', '日常',
--     'style', COALESCE(speech_style, ''),
--     'sample', COALESCE(sample_dialogue, '')
--   )
-- ]::jsonb
-- WHERE speech_style IS NOT NULL OR sample_dialogue IS NOT NULL;
